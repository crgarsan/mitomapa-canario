"""Exercise the browser lock with pip using inert, offline wheel fixtures."""

import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "requirements-browser-tests.txt"
ENTRY = re.compile(
    r"([A-Za-z][A-Za-z0-9_-]*)==(\d+\.\d+\.\d+)"
    r"((?:\s+--hash=sha256:[0-9a-f]{64})+)"
)
EXPECTED = {
    "playwright": "1.64.0",
    "pillow": "13.0.0",
    "lxml": "6.1.3",
    "pyee": "14.0.0",
    "greenlet": "3.5.6",
    "typing-extensions": "4.16.0",
}
# These are the runtime edges in the locked releases' PyPI wheel metadata.
DEPENDENCIES = {
    "playwright": ("pyee>=13,<15", "greenlet>=3.1.1,<4.0.0"),
    "pyee": ("typing-extensions",),
}


def lock_entries(test):
    text = "\n".join(line for line in LOCK.read_text().splitlines()
                     if line.strip() and not line.lstrip().startswith("#"))
    logical_lines = re.sub(r"\\\n\s*", " ", text).splitlines()
    entries = {}
    for line in logical_lines:
        match = ENTRY.fullmatch(line.strip())
        test.assertIsNotNone(match, "Each package needs an exact version and SHA-256 hashes")
        name, version, hashes = match.groups()
        name = name.lower().replace("_", "-")
        test.assertNotIn(name, entries, "Duplicate packages make lock review ambiguous")
        digests = re.findall(r"--hash=sha256:([0-9a-f]{64})", hashes)
        test.assertEqual(len(digests), len(set(digests)), "Duplicate artifact hashes")
        entries[name] = (version, line.strip())
    return entries


def inert_wheel(directory, name, version):
    """Only metadata is present: pip never builds or executes a fixture."""
    stem = f"{name.replace('-', '_')}-{version}"
    wheel = directory / f"{stem}-py3-none-any.whl"
    metadata = (f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n"
                + "".join(f"Requires-Dist: {edge}\n" for edge in DEPENDENCIES.get(name, ())))
    with ZipFile(wheel, "w") as archive:
        archive.writestr(f"{stem}.dist-info/METADATA", metadata + "\n")
        archive.writestr(f"{stem}.dist-info/WHEEL",
                         "Wheel-Version: 1.0\nGenerator: lock-test\n"
                         "Root-Is-Purelib: true\nTag: py3-none-any\n")
        archive.writestr(f"{stem}.dist-info/RECORD", "")
    return wheel


class PythonLockTests(unittest.TestCase):
    def test_browser_lock_pins_the_complete_hashed_dependency_closure(self):
        entries = lock_entries(self)
        self.assertEqual({name: entry[0] for name, entry in entries.items()}, EXPECTED)

    def test_offline_hash_install_contract_accepts_reviewed_bytes_and_rejects_a_changed_wheel(self):
        entries = lock_entries(self)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wheels = root / "wheels"
            wheels.mkdir()
            fixture_lines = []
            fixture_wheels = {}
            for name, (version, entry) in entries.items():
                wheel = inert_wheel(wheels, name, version)
                fixture_wheels[name] = wheel
                digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
                # Keep each production pin and option; only fixture bytes differ.
                fixture_lines.append(re.sub(r"sha256:[0-9a-f]{64}",
                                            "sha256:" + digest, entry))
            requirements = root / "requirements.txt"
            requirements.write_text("\n".join(fixture_lines) + "\n")
            command = [sys.executable, "-m", "pip", "--isolated", "download",
                       "--disable-pip-version-check", "--no-cache-dir", "--no-index",
                       "--find-links", str(wheels), "--require-hashes",
                       "--only-binary=:all:", "-r", str(requirements)]
            accepted = subprocess.run(command + ["--dest", str(root / "accepted")],
                                      capture_output=True, text=True, timeout=60)
            self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
            self.assertEqual(len(list((root / "accepted").glob("*.whl"))), len(EXPECTED))

            with ZipFile(fixture_wheels["pyee"], "a") as archive:
                archive.writestr("changed.txt", "unreviewed wheel bytes\n")
            rejected = subprocess.run(command + ["--dest", str(root / "rejected")],
                                      capture_output=True, text=True, timeout=60)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("DO NOT MATCH THE HASHES", rejected.stdout + rejected.stderr)
            self.assertFalse((root / "rejected" / fixture_wheels["pyee"].name).exists())


if __name__ == "__main__":
    unittest.main()
