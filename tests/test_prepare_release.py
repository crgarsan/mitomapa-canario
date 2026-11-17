"""A release bundle preserves committed bytes and rejects untrusted inputs."""

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZIP_STORED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
try:
    import prepare_release
except ImportError:
    prepare_release = None


def archive_bytes(label):
    stream = BytesIO()
    with ZipFile(stream, "w", compression=ZIP_STORED) as archive:
        archive.writestr("content.txt", label)
    return stream.getvalue()


class PrepareReleaseTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(prepare_release, "The traceable release preparer is missing")
        self.temporary = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.root = self.parent / "source"
        self.root.mkdir()
        self.output = self.parent / "delivery"
        self.archives = {
            "downloads/rea.elpx": archive_bytes("Native Spanish"),
            "downloads/share.zip": archive_bytes("Spanish sharing"),
            "downloads/sources.zip": archive_bytes("Current sources"),
            "en/downloads/rea-en.elpx": archive_bytes("Native English"),
            "en/downloads/share-en.zip": archive_bytes("English sharing"),
            "downloads/pintaderas-3d/recreaciones.zip": archive_bytes("Seals"),
            "downloads/pintaderas-3d/sellos.zip": archive_bytes("Stamps"),
            "downloads/vasijas/coleccion.zip": archive_bytes("Vessels"),
        }
        self.version = {"web_version": "4.10.0", "rea_exelearning_version": "4.8.9"}
        self.rows = []
        for index, (name, data) in enumerate(self.archives.items()):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            if index < 5:
                self.rows.append({"product": "elpx" if name.endswith(".elpx") else "package",
                                  "language": "en" if name.startswith("en/") else "es", "path": name,
                                  "version": "4.8.9" if name.endswith(".elpx") else "4.10.0",
                                  "base_version": None, "bytes": len(data), "sha256": sha256(data).hexdigest(),
                                  "availability": "published"})
        (self.root / "VERSION.json").write_text(json.dumps(self.version))
        (self.root / "SHA256SUMS.txt").write_text("".join(
            f"{sha256(data).hexdigest()}  {name}\n" for name, data in sorted(self.archives.items())))
        self.git("init", "-q")
        self.git("config", "user.email", "release-test@example.invalid")
        self.git("config", "user.name", "Release fixture")
        self.commit = self.commit_all()
        self.addCleanup(patch.stopall)
        # These separate domain validators have their own tests and production
        # integration. Git, bounded reads, archives, bundle and hashes stay real.
        patch.object(prepare_release, "validate_readiness", return_value=None).start()
        patch.object(prepare_release, "metadata_outputs", return_value={}).start()
        patch.object(prepare_release, "metadata_products", side_effect=lambda root, version: self.rows).start()
        patch.object(prepare_release, "current_paths", side_effect=lambda root, version: frozenset(self.archives)).start()
        patch.object(prepare_release, "validate_historical", return_value=None).start()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True).stdout.decode().strip()

    def commit_all(self):
        self.git("add", "--all")
        self.git("commit", "-qm", "Fixture")
        return self.git("rev-parse", "HEAD")

    def prepare(self, **kwargs):
        return prepare_release.prepare_bundle(self.root, expected_commit=self.commit, output=self.output, **kwargs)

    def test_check_does_not_write_and_bundle_preserves_exact_archive_bytes(self):
        manifest = prepare_release.prepare_bundle(self.root, expected_commit=self.commit, check=True)
        self.assertFalse(self.output.exists())
        self.assertEqual(manifest["sourceCommit"], self.commit)
        self.assertEqual(manifest["proposedTag"], "web-v4.10.0-" + self.commit[:12])
        self.prepare()
        self.assertEqual({p.relative_to(self.output).as_posix() for p in self.output.rglob("*") if p.is_file()},
                         set(self.archives) | {"RELEASE_MANIFEST.json", "SHA256SUMS.txt", "RELEASE_NOTES.md"})
        for name, data in self.archives.items():
            self.assertEqual((self.output / name).read_bytes(), data)
        prepare_release.verify_bundle(self.output, self.commit, root=self.root)
        before = {p.relative_to(self.output): p.stat().st_mtime_ns for p in self.output.rglob("*")}
        self.prepare()
        self.assertEqual({p.relative_to(self.output): p.stat().st_mtime_ns for p in self.output.rglob("*")}, before)
        models = [row for row in manifest["files"] if row["product"] == "model_collection"]
        self.assertEqual(len(models), 3)
        self.assertTrue(all(row["version"] is None and row["webVersionReference"] == "4.10.0" for row in models))

    def test_requires_full_exact_git_head(self):
        for commit in (None, self.commit[:12], "f" * 40, self.commit.upper()):
            with self.subTest(commit=commit), self.assertRaises(ValueError):
                prepare_release.prepare_bundle(self.root, expected_commit=commit, check=True)
        self.assertFalse(self.output.exists())

    def test_rejects_unstaged_staged_and_untracked_source_changes(self):
        target = self.root / "VERSION.json"
        before = target.read_bytes()
        target.write_bytes(before + b"\n")
        with self.assertRaises(ValueError):
            self.prepare()
        self.git("add", "VERSION.json")
        with self.assertRaises(ValueError):
            self.prepare()
        self.git("reset", "--hard", "HEAD")
        (self.root / "unreviewed.json").write_text("{}")
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertFalse(self.output.exists())

    def test_rejects_missing_public_pin_even_if_committed(self):
        sums = self.root / "SHA256SUMS.txt"
        sums.write_text("\n".join(sums.read_text().splitlines()[1:]) + "\n")
        self.commit = self.commit_all()
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertFalse(self.output.exists())

    def test_refuses_symlink_output_and_nonempty_unowned_directory(self):
        self.output.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.prepare()
        self.output.unlink()
        self.output.mkdir()
        (self.output / "mine.txt").write_text("Keep this")
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual((self.output / "mine.txt").read_text(), "Keep this")

    def test_rejects_tampered_output_and_any_unlisted_file(self):
        self.prepare()
        target = self.output / "downloads/rea.elpx"
        target.write_bytes(b"altered")
        with self.assertRaises(ValueError):
            prepare_release.verify_bundle(self.output, self.commit, root=self.root)
        target.write_bytes(self.archives["downloads/rea.elpx"])
        extra = self.output / "extra.txt"
        extra.write_text("Unlisted")
        with self.assertRaises(ValueError):
            prepare_release.verify_bundle(self.output, self.commit, root=self.root)

    def test_verifies_crc_before_writing_even_for_hash_pinned_archive(self):
        name = "downloads/rea.elpx"
        damaged = bytearray(self.archives[name])
        offset = damaged.index(b"Native Spanish")
        damaged[offset] ^= 1
        self.archives[name] = bytes(damaged)
        (self.root / name).write_bytes(damaged)
        self.rows[0]["sha256"] = sha256(damaged).hexdigest()
        (self.root / "SHA256SUMS.txt").write_text("".join(
            f"{sha256(data).hexdigest()}  {path}\n" for path, data in sorted(self.archives.items())))
        self.commit = self.commit_all()
        with self.assertRaisesRegex(ValueError, "CRC|ZIP"):
            self.prepare()
        self.assertFalse(self.output.exists())

    def test_preserves_regional_and_multilingual_languages_from_product_metadata(self):
        self.rows[3]["language"] = "en-GB"
        self.rows[2]["language"] = "es/en-GB"
        manifest = prepare_release.prepare_bundle(self.root, expected_commit=self.commit, check=True)
        languages = {row["path"]: row["language"] for row in manifest["files"]}
        self.assertEqual(languages["en/downloads/rea-en.elpx"], "en-GB")
        self.assertEqual(languages["downloads/sources.zip"], "es/en-GB")
        self.prepare()
        prepare_release.verify_bundle(self.output, self.commit, root=self.root)

    def test_rejects_empty_duplicate_or_unsafe_product_language_tags(self):
        for language in ("", "/es", "es/", "es//en-GB", "es/es", "en-GB/EN-gb",
                         "en\nGB", "en-GB\r", "es en", "es_en", "<en>", "es/../en",
                         "en--GB", "en-", "e-GB"):
            with self.subTest(language=repr(language)):
                self.rows[0]["language"] = language
                with self.assertRaises(ValueError):
                    self.prepare()
                self.assertFalse(self.output.exists())

    def test_rejects_missing_metadata_for_a_native_product(self):
        self.rows.pop(0)
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertFalse(self.output.exists())

    def test_does_not_treat_git_assume_unchanged_as_byte_provenance(self):
        target = self.root / "VERSION.json"
        self.git("update-index", "--assume-unchanged", "VERSION.json")
        target.write_text(json.dumps({**self.version, "web_version": "99.0.0"}))
        self.assertEqual(self.git("status", "--porcelain"), "")
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertFalse(self.output.exists())

    def test_rejects_symlink_parent_without_writing_to_its_target(self):
        real_parent = self.parent / "real-parent"
        real_parent.mkdir()
        link = self.parent / "linked-parent"
        link.symlink_to(real_parent, target_is_directory=True)
        self.output = link / "delivery"
        with self.assertRaises(ValueError):
            self.prepare()
        self.assertEqual(list(real_parent.iterdir()), [])

    def test_rejects_damaged_nested_elpx_even_with_valid_outer_crc_and_public_pin(self):
        nested = bytearray(archive_bytes("Nested native project"))
        nested[nested.index(b"Nested native project")] ^= 1
        stream = BytesIO()
        with ZipFile(stream, "w", compression=ZIP_STORED) as archive:
            archive.writestr("project.elpx", nested)
        name = "downloads/share.zip"
        self.archives[name] = stream.getvalue()
        (self.root / name).write_bytes(self.archives[name])
        self.rows[1]["bytes"] = len(self.archives[name])
        self.rows[1]["sha256"] = sha256(self.archives[name]).hexdigest()
        (self.root / "SHA256SUMS.txt").write_text("".join(
            f"{sha256(data).hexdigest()}  {path}\n" for path, data in sorted(self.archives.items())))
        self.commit = self.commit_all()
        with self.assertRaisesRegex(ValueError, "CRC|ZIP"):
            self.prepare()
        self.assertFalse(self.output.exists())

    def test_forged_manifest_metadata_fails_even_after_rehashing_checksums(self):
        self.prepare()
        manifest_path = self.output / "RELEASE_MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["files"][0]["version"] = "99.0.0"
        manifest_path.write_text(json.dumps(manifest))
        names = set(self.archives) | {"RELEASE_MANIFEST.json", "RELEASE_NOTES.md"}
        (self.output / "SHA256SUMS.txt").write_text("".join(
            f"{sha256((self.output / name).read_bytes()).hexdigest()}  {name}\n" for name in sorted(names)))
        with self.assertRaises(ValueError):
            prepare_release.verify_bundle(self.output, self.commit, root=self.root)


if __name__ == "__main__":
    unittest.main()
