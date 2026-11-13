"""Exercise current maintenance contracts without rewriting public releases."""

from contextlib import redirect_stdout
from io import BytesIO, StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZIP_DEFLATED


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import harden_drawing_archives as drawings
import harden_jspdf_exports as pdf
from release_support import digest, json_bytes, sums_bytes


def archive_bytes(files):
    output = BytesIO()
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for name, payload in files.items():
            archive.writestr(name, payload)
    return output.getvalue()


class MaintenanceToolsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = (ROOT / "scripts.js").read_text()
        with ZipFile(ROOT / "downloads/MitoMapa_canario_GobCan.elpx") as archive:
            cls.loaders = {name: archive.read(name) for name in pdf.SCRIPT_PATHS}

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "downloads").mkdir()

    def write_release(self, archives):
        for name, payload in archives.items():
            (self.root / name).write_bytes(payload)
        (self.root / "SHA256SUMS.txt").write_bytes(sums_bytes(archives))
        current = "downloads/current.elpx"
        if current in archives:
            payload = archives[current]
            (self.root / "VERSION.json").write_bytes(json_bytes({
                "download": {"path": current, "sha256": digest(payload), "bytes": len(payload)},
                "presets": [],
            }))

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob("*") if p.is_file()}

    def test_public_inventory_uses_verified_manifest_without_a_fixed_count(self):
        archives = {
            "downloads/current.elpx": archive_bytes(self.loaders),
            "downloads/source.zip": archive_bytes({"README.md": b"Reusable sources"}),
            "downloads/previous.elpx": archive_bytes(self.loaders),
        }
        self.write_release(archives)
        before = self.snapshot()
        result = pdf.verify_public_archives(self.root)
        self.assertEqual(result["public_archives"], 3)
        self.assertEqual(result["loaders"], 6)
        self.assertEqual(self.snapshot(), before)

    def test_public_inventory_rejects_unlisted_or_changed_archives(self):
        self.write_release({"downloads/current.elpx": archive_bytes(self.loaders)})
        (self.root / "downloads/unlisted.zip").write_bytes(archive_bytes({"extra": b"x"}))
        with self.assertRaisesRegex(ValueError, "inventory"):
            pdf.public_archives(self.root)
        (self.root / "downloads/unlisted.zip").unlink()
        (self.root / "downloads/current.elpx").write_bytes(archive_bytes({"extra": b"changed"}))
        with self.assertRaisesRegex(ValueError, "Checksum"):
            pdf.public_archives(self.root)

    def test_current_native_release_requires_all_reviewed_loaders(self):
        missing = {name: data for name, data in self.loaders.items() if "rubric" not in name}
        self.write_release({"downloads/current.elpx": archive_bytes(missing)})
        with self.assertRaisesRegex(ValueError, "current.*loaders"):
            pdf.verify_public_archives(self.root)

    def test_nested_loader_cannot_replace_a_missing_current_native_loader(self):
        missing = {name: data for name, data in self.loaders.items() if "rubric" not in name}
        progress = "idevices/progress-report/progress-report.js"
        missing["extra.zip"] = archive_bytes({progress: self.loaders[progress]})
        self.write_release({"downloads/current.elpx": archive_bytes(missing)})
        with self.assertRaisesRegex(ValueError, "current.*loaders"):
            pdf.verify_public_archives(self.root)

    def test_public_inventory_rejects_tampered_sri_in_a_nested_release(self):
        broken = {name: data.replace(pdf.INTEGRITY.encode(), b"sha384-changed")
                  for name, data in self.loaders.items()}
        self.write_release({
            "downloads/current.elpx": archive_bytes(self.loaders),
            "downloads/outer.zip": archive_bytes({"nested.elpx": archive_bytes(broken)}),
        })
        with self.assertRaisesRegex(ValueError, "integrity"):
            pdf.verify_public_archives(self.root)

    def test_pdf_global_cli_cannot_rewrite_archived_releases(self):
        self.write_release({"downloads/current.elpx": archive_bytes(self.loaders)})
        before = self.snapshot()
        with patch.object(pdf, "ROOT", self.root), patch.object(sys, "argv", ["harden_jspdf_exports.py"]):
            with self.assertRaisesRegex(ValueError, "read-only"):
                pdf.main()
        self.assertEqual(self.snapshot(), before)

    def test_single_artifact_cli_remains_standalone_with_its_reviewed_manifest(self):
        (self.root / "tools").mkdir()
        script = self.root / "tools/harden_jspdf_exports.py"
        script.write_bytes((ROOT / "tools/harden_jspdf_exports.py").read_bytes())
        (self.root / "JSPDF_DEPENDENCY.json").write_bytes((ROOT / "JSPDF_DEPENDENCY.json").read_bytes())
        artifact = self.root / "downloads/new-editor-copy.elpx"
        artifact.write_bytes(archive_bytes(self.loaders))
        selected = self.root / "selected-editor-copy.elpx"
        selected.symlink_to(artifact)
        result = subprocess.run([sys.executable, str(script), "--artifact", str(selected), "--check"],
                                cwd=self.root, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["loaders"], 3)

    def write_delivery(self, *, extra_archive=False):
        delivery = self.root / "delivery"
        (delivery / "documentacion").mkdir(parents=True)
        native = "MitoMapa_canario_GobCan.elpx"
        exported = "MitoMapa_canario_GobCan_HTML.zip"
        validation = "VALIDACION_GOBCAN.txt"
        files = {
            native: archive_bytes({**self.loaders, "scripts.js": self.script.encode()}),
            exported: archive_bytes(self.loaders),
            "documentacion/guia.txt": "Guía de aula".encode(),
        }
        files[validation] = (f"ELPX SHA-256: {digest(files[native])}\n"
                             f"HTML ZIP SHA-256: {digest(files[exported])}\n").encode()
        (self.root / "downloads" / native).write_bytes(files[native])
        if extra_archive:
            files["Material de clase.zip"] = archive_bytes({"guia.txt": b"Classroom notes"})
        files["SHA256SUMS.txt"] = sums_bytes(files)
        files["Entrega_MitoMapa_GobCan.zip"] = archive_bytes(files)
        for name, payload in files.items():
            (delivery / name).write_bytes(payload)
        return delivery

    def check_delivery(self, module, delivery):
        with patch.object(module, "ROOT", self.root):
            if module is pdf:
                pdf.delivery_update(delivery, True)
            else:
                drawings.verify_delivery(delivery, drawings.drawing_policy(self.script))

    def test_delivery_checks_accept_regular_files_and_nested_documents_read_only(self):
        delivery = self.write_delivery(extra_archive=True)
        before = self.snapshot()
        for module in (pdf, drawings):
            with self.subTest(module=module.__name__):
                self.check_delivery(module, delivery)
        self.assertEqual(self.snapshot(), before)

    def test_delivery_reader_caps_control_text_without_reading_archive_contents(self):
        delivery = self.write_delivery()
        with pdf.DeliveryFiles(delivery) as files, patch.object(pdf, "DELIVERY_TEXT_LIMIT", 32):
            with self.assertRaisesRegex(ValueError, "size limit"):
                files.read("SHA256SUMS.txt")

    def test_delivery_reader_requires_canonical_relative_names(self):
        delivery = self.write_delivery()
        with pdf.DeliveryFiles(delivery) as files:
            for name in ("documentacion//guia.txt", "documentacion/./guia.txt",
                         "documentacion/../SHA256SUMS.txt", "documentacion\\guia.txt",
                         str(delivery / "SHA256SUMS.txt"), "SHA256SUMS.txt\0"):
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Unsafe asset path"):
                    files.read(name)

    def test_delivery_reader_keeps_containment_checks_without_descriptor_walk(self):
        delivery = self.write_delivery()
        guide = delivery / "documentacion" / "guia.txt"
        guide.with_name("guia-enlace.txt").symlink_to(guide)
        with patch.object(os, "supports_dir_fd", set()), pdf.DeliveryFiles(delivery) as files:
            self.assertEqual(files.read("documentacion/guia.txt"), "Guía de aula".encode())
            self.assertIn("MitoMapa_canario_GobCan.elpx", files.archive_names())
            with self.assertRaisesRegex(ValueError, "without symlinks"):
                files.read("documentacion/guia-enlace.txt")

    def test_delivery_checks_require_regular_unlinked_artifacts(self):
        delivery = self.write_delivery(extra_archive=True)
        for module, name in (
            (pdf, "MitoMapa_canario_GobCan.elpx"),
            (pdf, "MitoMapa_canario_GobCan_HTML.zip"),
            (pdf, "Entrega_MitoMapa_GobCan.zip"),
            (pdf, "VALIDACION_GOBCAN.txt"),
            (pdf, "SHA256SUMS.txt"),
            (pdf, "documentacion"),
            (drawings, "MitoMapa_canario_GobCan.elpx"),
            (drawings, "Material de clase.zip"),
            (drawings, "SHA256SUMS.txt"),
            (drawings, "documentacion"),
        ):
            with self.subTest(module=module.__name__, name=name):
                original = delivery / name
                renamed = original.with_suffix(original.suffix + ".copy")
                original.rename(renamed)
                try:
                    original.symlink_to(renamed, target_is_directory=renamed.is_dir())
                    with self.assertRaisesRegex(ValueError, "without symlinks"):
                        self.check_delivery(module, delivery)
                finally:
                    original.unlink()
                    renamed.rename(original)

    def test_delivery_checks_reject_a_selected_directory_link(self):
        delivery = self.write_delivery()
        link = delivery.with_name("selected-delivery")
        link.symlink_to(delivery, target_is_directory=True)
        native = "MitoMapa_canario_GobCan.elpx"
        payload = (delivery / native).read_bytes()
        self.write_release({f"downloads/{native}": payload, "downloads/current.elpx": payload})
        (self.root / "scripts.js").write_text(self.script)
        for module in (pdf, drawings):
            with self.subTest(module=module.__name__), patch.object(module, "ROOT", self.root), patch.object(
                    sys, "argv", [module.__name__, "--check", "--delivery-dir", str(link)]):
                with self.assertRaisesRegex(ValueError, "without symlinks"):
                    module.main()

    def test_drawing_policy_allows_changes_outside_security_boundaries(self):
        verify = drawings.drawing_policy(self.script)
        verify(self.script + "\n// A later, unrelated classroom interface change.\n")
        historical_import = self.script.replace("  clearLearnerResponses();\n", "")
        verify(historical_import)

    def test_drawing_policy_rejects_tampered_decoder_and_restore_guards(self):
        verify = drawings.drawing_policy(self.script)
        mutations = [
            self.script.replace("137,80,78,71", "138,80,78,71", 1),
            self.script.replace("width:900,height:520", "width:9000,height:5200", 1),
            self.script.replace("safeWorkshopDrawing(source.drawing)", "source.drawing", 1),
            self.script.replace("loadWorkshopDrawing(imageData)", "Promise.resolve(new Image())", 1),
        ]
        for index, broken in enumerate(mutations):
            with self.subTest(mutation=index), self.assertRaises(ValueError):
                verify(broken)

    def test_drawing_policy_checks_nested_scripts_without_git_history(self):
        verify = drawings.drawing_policy(self.script)
        nested = archive_bytes({"content/resources/mitomapa/scripts.js": self.script.encode()})
        outer = archive_bytes({"native.elpx": nested, "README.md": b"Resource"})
        with patch.object(drawings, "original_root", side_effect=AssertionError("History unavailable")):
            self.assertEqual(drawings.verify_drawing_archive(outer, verify), (1, 1))
        damaged = archive_bytes({"scripts.js": self.script.replace(
            "137,80,78,71", "138,80,78,71", 1).encode()})
        with self.assertRaises(ValueError):
            drawings.verify_drawing_archive(archive_bytes({"nested.zip": damaged}), verify)

    def test_drawing_policy_rejects_mutation_before_normalization_or_unsafe_assignment(self):
        verify = drawings.drawing_policy(self.script)
        preparation = "const importedWorkshop=await normalizeImportedDrawings(sanitizeImportedWorkshop(payload.workshop));"
        early_mutation = self.script.replace(preparation, "clearLearnerResponses();\n  " + preparation, 1)
        unsafe_assignment = self.script.replace("workshopState=importedWorkshop;", "workshopState=payload.workshop;", 1)
        for broken in (early_mutation, unsafe_assignment):
            with self.assertRaises(ValueError):
                verify(broken)

    def test_drawing_policy_rejects_a_later_second_assignment_of_unchecked_workshop(self):
        verify = drawings.drawing_policy(self.script)
        for assignment in ("workshopState=payload.workshop;", "workshopState&&=payload.workshop;"):
            appended_assignment = self.script.replace("workshopState=importedWorkshop;",
                                                      "workshopState=importedWorkshop;\n  " + assignment, 1)
            with self.subTest(assignment=assignment), self.assertRaisesRegex(ValueError, "assignment"):
                verify(appended_assignment)

    def test_drawing_global_cli_is_read_only_and_independent_of_history(self):
        archives = {"downloads/source.zip": archive_bytes({"scripts.js": self.script.encode()})}
        self.write_release(archives)
        (self.root / "scripts.js").write_text(self.script)
        before = self.snapshot()
        with patch.object(drawings, "ROOT", self.root), patch.object(sys, "argv", ["drawings.py", "--check"]), \
                patch.object(drawings, "original_root", side_effect=AssertionError("History unavailable")):
            with redirect_stdout(StringIO()) as captured:
                drawings.main()
        self.assertEqual(json.loads(captured.getvalue())["drawing_scripts"], 1)
        self.assertEqual(self.snapshot(), before)
        with patch.object(drawings, "ROOT", self.root), patch.object(sys, "argv", ["drawings.py"]):
            with self.assertRaisesRegex(ValueError, "read-only"):
                drawings.main()
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
