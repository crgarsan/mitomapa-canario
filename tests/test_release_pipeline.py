"""Exercise release packaging boundaries with small, independent fixtures."""

from io import BytesIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from prepare_deploy import stage_assets
from release_support import (
    digest, json_bytes, metadata, parse_sums, read_zip, sums_bytes,
    verify_manifest, zip_bytes,
)
from update_release import DOCUMENTS, check_elpx, check_release, update_release


class ReleasePipelineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.version = {
            "web_version": "4.6.0", "rea_exelearning_version": "4.6.0",
            "previous_web_version": "4.5.1",
            "download": {"path": "downloads/MitoMapa_canario_GobCan.elpx"},
            "sharing_archive": {"path": "downloads/MitoMapa_REA_v4_6_0.zip"},
            "source_archive": {"path": "downloads/MitoMapa_fuentes_web_v4_6_0.zip"},
            "release_notes": "CAMBIOS_WEB_4_6_0.md",
            "rea_release_notes": "CAMBIOS_REA_4_6_0.md",
        }
        self.write("VERSION.json", json_bytes(self.version))
        self.write("index.html", b'<a rel="license" href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>')
        self.write("version.js", b'window.MitoMapaVersion={web:"4.6.0"};\n')
        self.write("itinerario.js", b"/* current route module */\n")
        self.write("tests/current_test.py", b"# current tests\n")
        self.write("tools/current_tool.py", b"# current tool\n")
        for name in (*DOCUMENTS, self.version["release_notes"], self.version["rea_release_notes"]):
            self.write(name, f"Current document {name}\n".encode())
        self.old_name = "downloads/MitoMapa_fuentes_web_v4_5_1.zip"
        self.old_payload = zip_bytes({"index.html": b"Historical content"})
        self.write(self.old_name, self.old_payload)
        portable = {name: (self.root / name).read_bytes() for name in ("index.html", "version.js", "VERSION.json")}
        portable["PORTABLE_MANIFEST.json"] = json_bytes({
            "web_version": "4.6.0", "files": sorted([*portable, "PORTABLE_MANIFEST.json"]),
            "assets": {name: metadata(data) for name, data in portable.items()},
        })
        elpx = {f"content/resources/mitomapa/{name}": data for name, data in portable.items()}
        elpx["content.xml"] = b"<ode/>"
        elpx["libs/elpx-manifest.js"] = b"window.__ELPX_MANIFEST__=" + json_bytes({
            "files": sorted([*elpx, "libs/elpx-manifest.js"]), "version": 1,
        }).rstrip() + b";\n"
        self.write(self.version["download"]["path"], zip_bytes(elpx))
        listed = {name: (self.root / name).read_bytes() for name in (self.old_name, "index.html", self.version["download"]["path"])}
        self.write("SHA256SUMS.txt", sums_bytes(listed))

    def write(self, name, payload):
        destination = self.root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)

    def snapshot(self):
        return {path.relative_to(self.root).as_posix(): (digest(path.read_bytes()), path.stat().st_mtime_ns)
                for path in self.root.rglob("*") if path.is_file()}

    def test_packages_preserve_history_and_check_is_read_only(self):
        update_release(self.root)
        self.assertEqual((self.root / self.old_name).read_bytes(), self.old_payload)
        public = parse_sums((self.root / "SHA256SUMS.txt").read_text())
        self.assertIn(self.old_name, public)
        sources = read_zip((self.root / self.version["source_archive"]["path"]).read_bytes())
        self.assertFalse(any(name.lower().endswith((".zip", ".elpx")) for name in sources))
        self.assertIn("itinerario.js", sources)
        self.assertIn("tests/current_test.py", sources)
        self.assertIn("tools/current_tool.py", sources)
        verify_manifest(sources, json.loads(sources["SOURCE_MANIFEST.json"]), {"SOURCE_MANIFEST.json"})
        sharing = read_zip((self.root / self.version["sharing_archive"]["path"]).read_bytes())
        internal_version = json.loads(sharing["documentacion/VERSION.json"])
        self.assertNotIn("sha256", internal_version["sharing_archive"])
        self.assertIn("sha256", internal_version["download"])
        before = self.snapshot()
        check_release(self.root)
        self.assertEqual(self.snapshot(), before)
        update_release(self.root)
        self.assertEqual({name: details[0] for name, details in self.snapshot().items()},
                         {name: details[0] for name, details in before.items()})

    def test_check_rejects_stale_sources_even_if_public_checksums_are_refreshed(self):
        update_release(self.root)
        self.write("itinerario.js", b"/* changed source not repackaged */\n")
        public = parse_sums((self.root / "SHA256SUMS.txt").read_text())
        self.write("SHA256SUMS.txt", sums_bytes({name: (self.root / name).read_bytes() for name in public}))
        with self.assertRaisesRegex(ValueError, "source archive is not synchronized"):
            check_release(self.root)

    def test_sharing_guides_have_local_styles_templates_and_editable_link(self):
        self.write("GUIA_DOCENTE.html", b'''<link href="styles.css"><link href="docente.css">
<a href="downloads/Rubrica_lectura_MitoMapa_4_0.html">Pauta</a>
<a href="index.html#recursos">Web</a>
<a href="downloads/MitoMapa_canario_GobCan.elpx">Editar</a>''')
        update_release(self.root)
        sharing = read_zip((self.root / self.version["sharing_archive"]["path"]).read_bytes())
        guide = sharing["documentacion/GUIA_DOCENTE.html"].decode()
        self.assertIn('href="styles.css"', guide)
        self.assertIn("documentacion/styles.css", sharing)
        self.assertIn("documentacion/docente.css", sharing)
        self.assertIn("documentacion/downloads/Rubrica_lectura_MitoMapa_4_0.html", sharing)
        self.assertIn('href="https://mitomapa-canario.cgarcias.workers.dev/index.html#recursos"', guide)
        self.assertIn('href="../MitoMapa_canario_GobCan.elpx"', guide)

    def test_historical_archives_cannot_be_silently_replaced(self):
        self.write(self.old_name, zip_bytes({"index.html": b"Different history"}))
        with self.assertRaisesRegex(ValueError, "Historical download changed"):
            update_release(self.root)

    def test_oversized_release_is_rejected_before_any_file_is_written(self):
        before = self.snapshot()
        with patch("update_release.MAX_ASSET_BYTES", 10):
            with self.assertRaisesRegex(ValueError, "25 MiB"):
                update_release(self.root)
        self.assertEqual(self.snapshot(), before)

    def test_oversize_or_bad_hash_preserves_existing_stage(self):
        output = self.root / ".deploy"
        output.mkdir()
        (output / "sentinel").write_text("previous deployment")
        with patch("release_support.MAX_ASSET_BYTES", 10):
            with self.assertRaisesRegex(ValueError, "25 MiB"):
                stage_assets(self.root, output)
        self.write("index.html", b"unrecorded modification")
        with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
            stage_assets(self.root, output)
        self.assertEqual((output / "sentinel").read_text(), "previous deployment")
        self.assertFalse(list(self.root.glob(".deploy-*")))

    def test_duplicate_and_traversal_members_are_rejected(self):
        for name in ("../escape", "/absolute", "folder/../escape", "C:/escape", "folder\\escape"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                read_zip(self.raw_zip([(name, b"x")]))
        with self.assertWarns(UserWarning):
            duplicate = self.raw_zip([("same", b"a"), ("same", b"b")])
        with self.assertRaisesRegex(ValueError, "Duplicate ZIP"):
            read_zip(duplicate)

    def test_native_delivery_rejects_an_embedded_web_or_a_different_license(self):
        version = {**self.version, "elpx_distribution": {"mode": "native_only"}}
        files = {
            "content.xml": b'''<ode xmlns="http://www.intef.es/xsd/ode"><odeProperty><key>pp_license</key><value>creative commons: attribution - share alike 4.0</value></odeProperty><odeNavStructure><odePageId>page</odePageId><odeComponent><odeIdeviceId>activity</odeIdeviceId></odeComponent></odeNavStructure></ode>''',
            "EDITORIAL_MANIFEST.json": json_bytes({
                "distribution": "native_only", "embedded_web_app": False,
                "edition": version["rea_exelearning_version"], "pages": ["page"],
                "idevices": ["activity"],
            }),
        }

        def payload():
            files["libs/elpx-manifest.js"] = b"window.__ELPX_MANIFEST__=" + json_bytes({
                "files": sorted(set(files) | {"libs/elpx-manifest.js"})}) + b";"
            return zip_bytes(files)

        check_elpx(payload(), version, self.root)
        files["content/resources/mitomapa/index.html"] = b"<p>Old embedded application</p>"
        with self.assertRaisesRegex(ValueError, "still contains the web"):
            check_elpx(payload(), version, self.root)
        del files["content/resources/mitomapa/index.html"]
        files["content.xml"] = files["content.xml"].replace(b"share alike 4.0", b"non commercial - share alike 4.0")
        with self.assertRaisesRegex(ValueError, "licence must be CC BY-SA 4.0"):
            check_elpx(payload(), version, self.root)

    @staticmethod
    def raw_zip(entries):
        output = BytesIO()
        with ZipFile(output, "w") as archive:
            for name, payload in entries:
                archive.writestr(name, payload)
        return output.getvalue()


if __name__ == "__main__":
    unittest.main()
