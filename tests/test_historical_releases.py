"""Historical migration checks exercise small real ZIP files and a Git snapshot."""

import copy
from dataclasses import replace
from io import BytesIO
import importlib
import json
import os
from pathlib import Path
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from zipfile import ZIP_STORED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import harden_jspdf_exports as archive_reader


class HistoricalReleasesTests(unittest.TestCase):
    def setUp(self):
        if not (ROOT / "tools/historical_releases.py").is_file():
            self.fail("The historical catalog builder and checker do not exist yet")
        self.api = importlib.import_module("historical_releases")
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.version = {
            "download": {"path": "downloads/current.elpx"},
            "sharing_archive": {"path": "downloads/current.zip"},
            "source_archive": {"path": "downloads/sources.zip"},
            "presets": [{"name": "Esencial", "path": "downloads/old.elpx"}],
            "compatibility_aliases": ["downloads/old.elpx"],
            "elpx_source": {"path": "downloads/old.elpx"},
        }
        for path in ("downloads/current.elpx", "downloads/current.zip", "downloads/sources.zip", "downloads/old.elpx", "downloads/older.zip"):
            self.archive(path)
        (self.root / "VERSION.json").write_text(json.dumps(self.version), encoding="utf-8")
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=Catalog test", "-c", "user.email=catalog@example.invalid", "commit", "-qm", "Source snapshot")
        self.commit = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True, text=True).stdout

    def archive(self, name, content=b"Original historical bytes"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(path, "w", compression=ZIP_STORED) as archive:
            archive.writestr("content.txt", content)

    def build(self):
        return self.api.build_catalog(self.root, source_commit=self.commit)

    def test_provenance_uses_the_same_bytes_as_hash_and_crc(self):
        target = self.root / "downloads/old.elpx"
        committed = target.read_bytes()
        self.archive("downloads/old.elpx", b"A different, valid historical ZIP")
        original_reader = self.api.read_archive_file

        def restore_after_read(path, *args, **kwargs):
            payload = original_reader(path, *args, **kwargs)
            if Path(path).resolve() == target.resolve():
                target.write_bytes(committed)
            return payload

        with patch.object(self.api, "read_archive_file", side_effect=restore_after_read):
            with self.assertRaisesRegex(ValueError, "Historical archive identity differs"):
                self.build()
        self.assertEqual(target.read_bytes(), committed)

    def test_build_catalog_excludes_current_and_preserves_consumers(self):
        catalog = self.build()
        self.assertEqual([item["originalPath"] for item in catalog["archives"]], ["downloads/old.elpx", "downloads/older.zip"])
        old = catalog["archives"][0]
        self.assertEqual(old["originalURL"], "https://mitomapacanario.org/downloads/old.elpx")
        self.assertEqual(old["sourceCommit"], self.commit)
        self.assertEqual(old["bytes"], (self.root / "downloads/old.elpx").stat().st_size)
        self.assertTrue(old["crcValid"])
        self.assertEqual(old["knownConsumers"], ["VERSION.json:compatibility_aliases[0]", "VERSION.json:elpx_source.path", "VERSION.json:presets[0].path"])
        self.assertTrue(old["requiresConsumerAdaptation"])
        self.assertEqual(old["destination"]["status"], "planned")
        self.assertFalse(old["destination"]["active"])
        self.assertEqual(old["destination"]["tag"], "archive-" + self.commit[:12])
        self.assertEqual(old["destination"]["assetName"], "old.elpx")
        self.api.check_catalog(self.root, catalog)

    def test_rejects_changed_historical_hash_even_when_size_is_equal(self):
        catalog = self.build()
        path = self.root / "downloads/old.elpx"
        original_size = path.stat().st_size
        # Rebuild a valid ZIP with equal-sized changed content: CRC remains valid,
        # so byte-identity validation, rather than malformed-ZIP rejection, must fail.
        self.archive("downloads/old.elpx", b"Modified historical bytes")
        self.assertEqual(path.stat().st_size, original_size)
        with self.assertRaisesRegex(ValueError, "identity|hash|source"):
            self.api.check_catalog(self.root, catalog)

    def test_rejects_current_archive_inserted_in_historical_inventory(self):
        catalog = self.build()
        catalog["archives"][0]["originalPath"] = "downloads/current.elpx"
        with self.assertRaisesRegex(ValueError, "current|inventory"):
            self.api.check_catalog(self.root, catalog)

    def test_rejects_missing_historical_archive(self):
        catalog = self.build()
        catalog["archives"].pop()
        with self.assertRaisesRegex(ValueError, "inventory"):
            self.api.check_catalog(self.root, catalog)

    def test_rejects_duplicate_original_path(self):
        catalog = self.build()
        catalog["archives"].append(copy.deepcopy(catalog["archives"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate|duplicate"):
            self.api.check_catalog(self.root, catalog)

    def test_rejects_unsafe_asset_name_and_unexpected_destination(self):
        catalog = self.build()
        for value in ("../old.elpx", "folder/old.elpx", "old?download.elpx"):
            with self.subTest(value=value):
                changed = copy.deepcopy(catalog)
                changed["archives"][0]["destination"]["assetName"] = value
                with self.assertRaisesRegex(ValueError, "asset|destination"):
                    self.api.check_catalog(self.root, changed)
        catalog["archives"][0]["destination"]["status"] = "published"
        with self.assertRaisesRegex(ValueError, "planned|destination"):
            self.api.check_catalog(self.root, catalog)

    def test_colliding_basenames_receive_unique_stable_safe_names(self):
        self.archive("another/older.zip", b"A different historical archive")
        self.git("add", ".")
        self.git("-c", "user.name=Catalog test", "-c", "user.email=catalog@example.invalid", "commit", "-qm", "Collision")
        self.commit = self.git("rev-parse", "HEAD").strip()
        catalog = self.build()
        matching = [item for item in catalog["archives"] if item["originalPath"].endswith("/older.zip")]
        names = [item["destination"]["assetName"] for item in matching]
        self.assertEqual(len(names), 2)
        self.assertEqual(len(set(names)), 2)
        self.assertTrue(all(name.startswith("path-") and name.endswith(".zip") for name in names))
        self.api.check_catalog(self.root, catalog)
        self.assertEqual(self.build(), catalog)

    def test_rejects_duplicate_destination_name(self):
        catalog = self.build()
        catalog["archives"][1]["destination"]["assetName"] = catalog["archives"][0]["destination"]["assetName"]
        with self.assertRaisesRegex(ValueError, "Duplicate|duplicate"):
            self.api.check_catalog(self.root, catalog)

    def test_invalid_crc_is_rejected_without_extracting(self):
        self.archive("downloads/old.elpx", b"bad CRC payload")
        path = self.root / "downloads/old.elpx"
        path.write_bytes(path.read_bytes().replace(b"bad CRC payload", b"bad CRC payloae"))
        self.git("add", ".")
        self.git("-c", "user.name=Catalog test", "-c", "user.email=catalog@example.invalid", "commit", "-qm", "Corrupt archive")
        self.commit = self.git("rev-parse", "HEAD").strip()
        with self.assertRaisesRegex(ValueError, "CRC|ZIP"):
            self.build()

    def test_archive_directory_count_is_bounded_before_zipfile_constructor(self):
        output = BytesIO()
        with ZipFile(output, "w", compression=ZIP_STORED) as archive:
            for index in range(2001):
                archive.writestr(str(index), b"")
        ordinary = output.getvalue()
        end = ordinary.rindex(b"PK\x05\x06")
        understated = bytearray(ordinary)
        struct.pack_into("<HH", understated, end + 8, 1, 1)
        # Both the declared count and real directory records must be bounded;
        # a tiny EOCD count must not bypass the pre-constructor walk.
        for payload in (ordinary, bytes(understated)):
            (self.root / "downloads/older.zip").write_bytes(payload)
            with self.subTest(understated=payload != ordinary), patch.object(
                    ZipFile, "__init__", side_effect=AssertionError("ZIP parsed before member-count preflight")):
                with self.assertRaisesRegex(ValueError, "member count.*limit"):
                    self.api._archive_identity(self.root, "downloads/older.zip")

    def test_archive_input_read_is_bounded_when_file_stat_is_stale(self):
        class GrowingStream(BytesIO):
            def fileno(self):
                return 0

            def close(self):
                self.bytes_consumed = self.tell()
                super().close()

        stream = GrowingStream(b"123456789012")
        false_stat = SimpleNamespace(st_size=1, st_mode=stat.S_IFREG)
        limits = replace(archive_reader.DEFAULT_ARCHIVE_LIMITS, max_compressed_bytes=8)
        with patch.object(archive_reader, "DEFAULT_ARCHIVE_LIMITS", limits), patch.object(
                Path, "stat", return_value=false_stat), patch.object(
                os, "fstat", return_value=false_stat), patch(
                "builtins.open", return_value=stream), patch.object(
                ZipFile, "testzip", side_effect=AssertionError("Unbounded CRC pass")):
            with self.assertRaisesRegex(ValueError, "compressed input.*actual size limit"):
                self.api._archive_identity(self.root, "downloads/older.zip")
        self.assertEqual(stream.bytes_consumed, 9)

    def test_source_commit_provenance_is_byte_identity_not_filename(self):
        self.archive("downloads/old.elpx", b"New valid bytes with the same filename")
        with self.assertRaisesRegex(ValueError, "source|identity"):
            self.build()

    def test_current_archive_paths_use_version_and_all_present_companion_sets(self):
        for name in ("index-en.html",):
            (self.root / name).write_text("English", encoding="utf-8")
        companions = {
            "en/downloads/MitoMapa_Canary_Islands_EN.elpx",
            "en/downloads/MitoMapa_Canary_Islands_EN.zip",
            "downloads/pintaderas-3d/recreaciones.zip",
            "downloads/pintaderas-3d/sellos.zip",
            "downloads/vasijas/coleccion.zip",
        }
        for name in companions:
            self.archive(name)
        self.assertEqual(self.api.current_archive_paths(self.root, self.version), frozenset({
            "downloads/current.elpx", "downloads/current.zip", "downloads/sources.zip", *companions,
        }))

    def test_rejects_wrong_current_identity_in_version(self):
        self.version["download"]["sha256"] = "0" * 64
        (self.root / "VERSION.json").write_text(json.dumps(self.version), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "current|identity"):
            self.build()

    def test_check_and_rebuild_are_read_only_and_idempotent(self):
        catalog = self.build()
        (self.root / "HISTORICAL_RELEASES.json").write_text(json.dumps(catalog), encoding="utf-8")
        before = {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob("*") if p.is_file()}
        self.api.check_catalog(self.root)
        self.assertEqual(self.build(), catalog)
        after = {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_cli_check_does_not_modify_catalog_or_archives(self):
        catalog = self.build()
        catalog_path = self.root / "HISTORICAL_RELEASES.json"
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        before = catalog_path.read_bytes()
        result = subprocess.run([sys.executable, str(ROOT / "tools/historical_releases.py"), "--root", str(self.root), "--check"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(catalog_path.read_bytes(), before)
        catalog["archives"][0]["bytes"] += 1
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        rejected = subprocess.run([sys.executable, str(ROOT / "tools/historical_releases.py"), "--root", str(self.root), "--check"], capture_output=True, text=True)
        self.assertNotEqual(rejected.returncode, 0)


if __name__ == "__main__":
    unittest.main()
