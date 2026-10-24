"""Verify native PDF dependency policy without network access or credentials."""
import base64
import copy
from hashlib import sha256, sha384
from io import BytesIO
import json
from pathlib import Path
import subprocess
import struct
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import harden_jspdf_exports as policy


def archive_bytes(entries):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.comment = b"Native export preservation"
        for name, data in entries.items():
            info = zipfile.ZipInfo(name, (2026, 10, 9, 10, 12, 14))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            info.comment = b"Keep entry metadata"
            archive.writestr(info, data)
    return buffer.getvalue()


def editor_descriptor_archive(entries):
    """Create editor-like flag-8 entries with zero external attributes."""
    class Stream:
        def __init__(self):
            self.buffer = BytesIO()

        def write(self, data):
            return self.buffer.write(data)

        def tell(self):
            return self.buffer.tell()

        def flush(self):
            pass

    stream = Stream()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    data = bytearray(stream.buffer.getvalue())
    with zipfile.ZipFile(BytesIO(data)) as archive:
        position = archive.start_dir
        for info in archive.infolist():
            assert data[position:position + 4] == b"PK\x01\x02"
            data[position + 38:position + 42] = b"\0" * 4
            lengths = struct.unpack_from("<HHH", data, position + 28)
            position += 46 + sum(lengths)
    return bytes(data)


class JsPdfPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.public = sorted(path for path in (ROOT / "downloads").iterdir()
                            if path.suffix in (".zip", ".elpx"))
        with zipfile.ZipFile(ROOT / "downloads/MitoMapa_canario_GobCan.elpx") as archive:
            cls.scripts = {name: archive.read(name).decode("utf-8")
                           for name in policy.SCRIPT_PATHS}

    def test_manifest_and_verified_umd_bytes_agree(self):
        policy.verify_dependency_manifest()
        data = (ROOT / "tests/fixtures/jspdf-4.2.1.umd.min.js").read_bytes()
        self.assertEqual(len(data), policy.UMD_BYTES)
        self.assertEqual(sha256(data).hexdigest(), policy.UMD_SHA256)
        actual = "sha384-" + base64.b64encode(sha384(data).digest()).decode("ascii")
        self.assertEqual(actual, policy.INTEGRITY)

    def test_manifest_rejects_unreviewed_release_changes(self):
        original = json.loads((ROOT / "JSPDF_DEPENDENCY.json").read_text())
        for key, value in (("version", "4.2.2"), ("url", policy.OLD_URL),
                           ("integrity", "sha384-AAAA"), ("cross_origin", "use-credentials"),
                           ("umd_sha256", "0" * 64), ("npm_tarball_integrity", "sha512-AAAA")):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as directory:
                manifest = copy.deepcopy(original)
                manifest[key] = value
                path = Path(directory) / "dependency.json"
                path.write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    policy.verify_dependency_manifest(path)

    def test_all_public_and_nested_native_loaders_are_verified(self):
        # Publication 4.8.10 preserves all 63 prior public packages and adds
        # source and sharing ZIPs. The sharing ZIP embeds the identical
        # 4.8.5 ELPX; this web-only release adds no native snapshot.
        self.assertEqual(len(self.public), 65)
        affected = loaders = nested_elpx = direct_loaders = 0
        for path in self.public:
            with self.subTest(archive=path.name):
                count, nested = policy.verify_archive(path.read_bytes())
                affected += bool(count)
                loaders += count
                nested_elpx += nested
                if path.suffix == ".elpx":
                    direct_loaders += count
        self.assertEqual((affected, loaders, nested_elpx, direct_loaders), (44, 167, 37, 56))

    def test_native_loader_mutations_are_rejected(self):
        for name, original in self.scripts.items():
            mutations = {
                "unversioned": original.replace(policy.URL, policy.OLD_URL),
                "other_version": original.replace("jspdf@4.2.1/", "jspdf@4.2.2/"),
                "other_origin": original.replace("https://cdn.jsdelivr.net/", "https://example.com/"),
                "wrong_integrity": original.replace(policy.INTEGRITY, "sha384-AAAA"),
                "missing_integrity": original.replace(policy.ASSIGNMENTS[1] + "\n", ""),
                "wrong_cors": original.replace(policy.ASSIGNMENTS[2], "        s.crossOrigin = 'use-credentials';"),
                "missing_cors": original.replace(policy.ASSIGNMENTS[2] + "\n", ""),
                "late_integrity": original.replace(policy.ASSIGNMENTS[1] + "\n", "").replace(
                    policy.APPEND, policy.APPEND + "\n" + policy.ASSIGNMENTS[1]),
                "late_cors": original.replace(policy.ASSIGNMENTS[2] + "\n", "").replace(
                    policy.APPEND, policy.APPEND + "\n" + policy.ASSIGNMENTS[2]),
                "duplicate_override": original.replace(policy.APPEND,
                    "s.integrity = '';\n        " + policy.APPEND),
            }
            for mutation, damaged in mutations.items():
                with self.subTest(script=name, mutation=mutation):
                    with self.assertRaises(ValueError):
                        policy.verify_loader(damaged)

    def test_transform_preserves_native_functions_and_fallbacks(self):
        for name, hardened in self.scripts.items():
            with self.subTest(script=name):
                original = hardened.replace(policy.NEW_ASSIGNMENTS, policy.OLD_ASSIGNMENT)
                expected = original.replace(policy.OLD_ASSIGNMENT, policy.NEW_ASSIGNMENTS)
                self.assertEqual(policy.patch_loader(original), expected)
                self.assertEqual(policy.patch_loader(hardened), hardened)
                start, end = policy.loader_bounds(original)
                after_start, after_end = policy.loader_bounds(hardened)
                self.assertEqual(original[:start], hardened[:after_start])
                self.assertEqual(original[end:], hardened[after_end:])

    def test_recursive_update_preserves_other_member_bytes_and_zip_metadata(self):
        script_name = "idevices/progress-report/progress-report.js"
        original_script = self.scripts[script_name].replace(policy.NEW_ASSIGNMENTS, policy.OLD_ASSIGNMENT)
        native = archive_bytes({script_name: original_script.encode(),
                                "content.xml": b"native XML and activity IDs",
                                "libs/elpx-manifest.js": b"same inventory",
                                "media/narracion.mp3": b"original audio bytes"})
        outer = archive_bytes({"downloads/editor.elpx": native,
                               "scripts.js": b"historical web script",
                               "README.md": b"historical documentation"})
        updated, loaders, nested = policy.patched_archive(outer)
        self.assertEqual((loaders, nested), (1, 1))
        self.assertEqual(policy.verify_archive(updated), (1, 1))
        outer_infos, outer_before, comment = policy.read_archive(outer)
        updated_infos, outer_after, updated_comment = policy.read_archive(updated)
        self.assertEqual(comment, updated_comment)
        for name in ("scripts.js", "README.md"):
            self.assertEqual(outer_before[name], outer_after[name])
        native_infos, native_before, comment = policy.read_archive(native)
        after_infos, native_after, after_comment = policy.read_archive(outer_after["downloads/editor.elpx"])
        self.assertEqual(native_before.keys(), native_after.keys())
        self.assertEqual(comment, after_comment)
        self.assertEqual(native_after[script_name], self.scripts[script_name].encode())
        for name in native_before.keys() - {script_name}:
            self.assertEqual(native_before[name], native_after[name])
        for old, new in zip(outer_infos + native_infos, updated_infos + after_infos, strict=True):
            for field in policy.ZIP_INFO_FIELDS:
                self.assertEqual(getattr(old, field), getattr(new, field))
        self.assertEqual(policy.patched_archive(updated)[0], updated)

    def test_unreviewed_loader_path_and_unknown_source_are_rejected(self):
        script = next(iter(self.scripts.values()))
        for name, data in (("unreviewed.js", script.encode()),
                           ("unknown.js", b"script.src = 'https://example.com/jspdf.umd.min.js';")):
            with self.subTest(path=name), self.assertRaises(ValueError):
                policy.verify_archive(archive_bytes({name: data}))

    def test_editor_data_descriptor_flags_and_zero_attributes_are_preserved(self):
        name = "idevices/rubric/rubric.js"
        old = self.scripts[name].replace(policy.NEW_ASSIGNMENTS, policy.OLD_ASSIGNMENT)
        before = editor_descriptor_archive({name: old.encode(), "content.xml": b"native content"})
        after, count, nested = policy.patched_archive(before)
        self.assertEqual((count, nested), (1, 0))
        before_infos, before_files, comment = policy.read_archive(before)
        after_infos, after_files, after_comment = policy.read_archive(after)
        self.assertEqual(after_files["content.xml"], before_files["content.xml"])
        for old_info, new_info in zip(before_infos, after_infos, strict=True):
            self.assertEqual(old_info.flag_bits, 8)
            self.assertEqual(old_info.external_attr, 0)
            for field in policy.ZIP_INFO_FIELDS:
                self.assertEqual(getattr(old_info, field), getattr(new_info, field))

    def test_editor_artifact_check_is_read_only_and_requires_reapplication(self):
        name = "idevices/checklist/checklist.js"
        old = self.scripts[name].replace(policy.NEW_ASSIGNMENTS, policy.OLD_ASSIGNMENT)
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "editor-export.elpx"
            artifact.write_bytes(archive_bytes({name: old.encode(), "content.xml": b"native project"}))
            command = [sys.executable, str(ROOT / "tools/harden_jspdf_exports.py"), "--artifact", str(artifact)]
            before = artifact.read_bytes()
            rejected = subprocess.run(command + ["--check"], capture_output=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(artifact.read_bytes(), before)
            subprocess.run(command, check=True, capture_output=True)
            hardened = artifact.read_bytes()
            subprocess.run(command + ["--check"], check=True, capture_output=True)
            self.assertEqual(artifact.read_bytes(), hardened)
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(artifact.read_bytes(), hardened)

    def test_release_download_and_preset_hashes_match(self):
        version = json.loads((ROOT / "VERSION.json").read_text())
        for record in [version["download"], *version["presets"]]:
            with self.subTest(path=record["path"]):
                data = (ROOT / record["path"]).read_bytes()
                self.assertEqual(record["bytes"], len(data))
                self.assertEqual(record["sha256"], sha256(data).hexdigest())

    def test_current_source_download_can_harden_a_fresh_editor_export(self):
        version = json.loads((ROOT / "VERSION.json").read_text())
        member = "idevices/checklist/checklist.js"
        old = self.scripts[member].replace(policy.NEW_ASSIGNMENTS, policy.OLD_ASSIGNMENT)
        with zipfile.ZipFile(ROOT / version["source_archive"]["path"]) as sources, tempfile.TemporaryDirectory() as directory:
            unpacked = Path(directory)
            for path in ("tools/build_elpx.py", "tools/harden_jspdf_exports.py", "JSPDF_DEPENDENCY.json"):
                data = sources.read(path)
                self.assertEqual(data, (ROOT / path).read_bytes())
                destination = unpacked / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
            artifact = unpacked / "fresh-export.elpx"
            artifact.write_bytes(archive_bytes({member: old.encode(), "content.xml": b"native project"}))
            command = [sys.executable, str(unpacked / "tools/harden_jspdf_exports.py"),
                       "--artifact", str(artifact)]
            subprocess.run(command, cwd=unpacked, check=True, capture_output=True)
            subprocess.run(command + ["--check"], cwd=unpacked, check=True, capture_output=True)
            self.assertEqual(policy.verify_archive(artifact.read_bytes()), (1, 0))


if __name__ == "__main__":
    unittest.main()
