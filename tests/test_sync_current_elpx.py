"""Protect the native project and media while refreshing its local web app."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from lxml import etree, html


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from release_support import digest, read_zip, zip_bytes
from harden_jspdf_exports import ZIP_INFO_FIELDS, read_archive
from native_preservation import verify_component
from sync_current_elpx import (
    APP, MEDIA_EXTENSIONS, NS, PORTABLE, MERGED_TEACHER_PAGES, build_archive, build_current, field,
    native_structure, synchronize, version_module,
)


class SynchronizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result, cls.version = build_current()
        cls.baseline = read_zip((ROOT / cls.version["elpx_source"]["path"]).read_bytes())
        cls.before = native_structure(cls.baseline)
        cls.after = native_structure(cls.result)

    def test_native_structure_and_all_untouched_activities_are_preserved(self):
        self.assertEqual(len(self.after["pages"]), 34)
        self.assertEqual(len(self.after["components"]), 118)
        self.assertEqual(set(self.before["pages"]) - set(self.after["pages"]), MERGED_TEACHER_PAGES)
        self.assertEqual(set(self.before["components"]), set(self.after["components"]))
        unchanged = 0
        games = 0
        for iid, original in self.before["components"].items():
            if field(original, "odeIdeviceTypeName") == "text":
                continue
            with self.subTest(idevice=iid):
                verify_component(original, self.after["components"][iid], self.result)
            unchanged += 1
            if field(original, "odeIdeviceTypeName") in {"puzzle", "scrambled-list", "quick-questions", "trueorfalse", "relate", "complete"}:
                games += 1
        self.assertEqual(unchanged, 55)
        self.assertEqual(games, 42)

    def test_all_existing_scenes_audio_and_runtime_dependencies_are_byte_identical(self):
        scenes = audio = 0
        for name, payload in self.baseline.items():
            if Path(name).suffix.lower() in MEDIA_EXTENSIONS or (
                    name.startswith(("libs/", "idevices/", "theme/")) and name != "libs/elpx-manifest.js"):
                with self.subTest(asset=name):
                    self.assertEqual(digest(self.result[name]), digest(payload))
            if Path(name).name.startswith("scene_"):
                scenes += 1
            if name.startswith(PORTABLE + "assets/audio/") and name.endswith(".mp3"):
                audio += 1
        self.assertEqual(scenes, 16)
        self.assertEqual(audio, 16)

    def test_edited_text_matches_its_editable_preview_search_and_export(self):
        source = self.result["search_index.js"].decode()
        search = json.loads(source[source.index("{"):].rstrip(";\n"))
        native = self.after["components"]
        compared = 0
        for page in search.values():
            document = html.fromstring(self.result[page["fileUrl"]])
            for block in page["blocks"].values():
                for iid, entry in block["idevices"].items():
                    if field(native[iid], "odeIdeviceTypeName") != "text":
                        continue
                    with self.subTest(idevice=iid):
                        editable = json.loads(field(native[iid], "jsonProperties"))["textTextarea"]
                        preview = html.fragment_fromstring(field(native[iid], "htmlView"))
                        editor_text = " ".join(html.fragment_fromstring(editable, create_parent=True).text_content().split())
                        preview_text = " ".join(preview.xpath(".//div[@class='exe-text-activity']/div")[0].text_content().split())
                        search_text = " ".join(html.fragment_fromstring(entry["htmlView"]).text_content().split())
                        export_text = " ".join(document.xpath(f'//div[@id="{iid}"]')[0].text_content().split())
                        self.assertEqual(editor_text, preview_text)
                        self.assertEqual(editor_text, search_text)
                        self.assertEqual(editor_text, export_text)
                        self.assertEqual(entry["jsonProperties"], field(native[iid], "jsonProperties"))
                        for reference in html.fragment_fromstring(editable, create_parent=True).xpath(".//@href | .//@src"):
                            if reference.startswith(APP):
                                self.assertNotIn("#", reference)
                                self.assertNotIn("?", reference)
                                self.assertIn(reference.removeprefix("{{context_path}}/"), self.result)
                    compared += 1
        self.assertEqual(compared, 63)
        guide = json.loads(field(native["20260823155837TGUID1"], "jsonProperties"))["textTextarea"]
        self.assertIn("multinivel", guide)

    def test_native_distribution_excludes_the_web_application(self):
        self.assertNotIn(PORTABLE + "index.html", self.result)
        self.assertFalse(any(name.startswith(PORTABLE) and Path(name).suffix.lower() not in MEDIA_EXTENSIONS for name in self.result))
        manifest = json.loads(self.result["EDITORIAL_MANIFEST.json"])
        self.assertEqual(manifest["distribution"], "native_only")
        self.assertFalse(manifest["embedded_web_app"])
        self.assertEqual(manifest["edition"], self.version["rea_exelearning_version"])
        self.assertEqual(set(manifest["pages"]), set(self.after["pages"]))
        self.assertEqual(set(manifest["idevices"]), set(self.after["components"]))
        self.assertFalse(any(name.endswith((".zip", ".elpx")) for name in self.result))

    def test_release_metadata_generates_the_web_version_module(self):
        next_version = copy.deepcopy(self.version)
        next_version.update(web_version="4.8.0", rea_exelearning_version="4.8.1")
        module = version_module(next_version).decode()
        values = json.loads(module.split("Object.freeze(", 1)[1].removesuffix(");\n"))
        self.assertEqual(values, {"version": "4.8.0", "reaVersion": "4.8.1", "schemaVersion": 1})
        script = (ROOT / "scripts.js").read_text()
        self.assertIn("const RESOURCE_VERSION=typeof window.MitoMapaVersion?.version", script)
        self.assertIn('app:"mitomapa-canario",version:RESOURCE_VERSION', script)

    def test_editor_zip_metadata_is_preserved_and_output_is_deterministic(self):
        first = build_archive(ROOT, self.version, self.result)
        self.assertEqual(first, build_archive(ROOT, self.version, self.result))
        original_infos, _, original_comment = read_archive((ROOT / self.version["elpx_source"]["path"]).read_bytes())
        current_infos, _, current_comment = read_archive(first)
        by_name = {info.filename: info for info in current_infos}
        self.assertEqual(original_comment, current_comment)
        for original in original_infos:
            if original.filename not in self.result:
                continue
            with self.subTest(member=original.filename):
                self.assertEqual({name: getattr(original, name) for name in ZIP_INFO_FIELDS},
                                 {name: getattr(by_name[original.filename], name) for name in ZIP_INFO_FIELDS})

    def test_check_does_not_write_or_repair_a_stale_archive(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "current.elpx"
            files = {"unchanged": b"current"}
            version = {"download": {"path": path.name}, "web_version": "4.6.0", "rea_exelearning_version": "4.6.0"}
            (root / "version.js").write_bytes(version_module(version))
            path.write_bytes(zip_bytes(files))
            before = path.read_bytes(), path.stat().st_mtime_ns
            with patch("sync_current_elpx.build_current", return_value=(files, version)), patch("sync_current_elpx.verify_zip_info"):
                synchronize(root, check=True)
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)
            with patch("sync_current_elpx.build_current", return_value=({"unchanged": b"different"}, version)):
                with self.assertRaisesRegex(ValueError, "not synchronized"):
                    synchronize(root, check=True)
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)
            (root / "version.js").write_bytes(b"stale manual version")
            with patch("sync_current_elpx.build_current", return_value=(files, version)):
                with self.assertRaisesRegex(ValueError, "release module is not synchronized"):
                    synchronize(root, check=True)
            self.assertEqual((root / "version.js").read_bytes(), b"stale manual version")

    def test_oversize_elpx_does_not_update_the_root_version_module(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            version = {"download": {"path": "current.elpx"}, "web_version": "4.6.1", "rea_exelearning_version": "4.6.1"}
            (root / "version.js").write_bytes(b"previous module")
            (root / "current.elpx").write_bytes(b"previous editable")
            with patch("sync_current_elpx.build_current", return_value=({}, version)), \
                    patch("sync_current_elpx.build_archive", return_value=b"oversized"), \
                    patch("sync_current_elpx.MAX_ASSET_BYTES", 3):
                with self.assertRaisesRegex(ValueError, "25 MiB"):
                    synchronize(root)
            self.assertEqual((root / "version.js").read_bytes(), b"previous module")
            self.assertEqual((root / "current.elpx").read_bytes(), b"previous editable")


if __name__ == "__main__":
    unittest.main()
