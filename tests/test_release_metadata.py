"""Release descriptions follow VERSION.json without modifying learning packages."""

from pathlib import Path
from html.parser import HTMLParser
import json
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import release_metadata
from release_support import json_bytes, metadata, zip_bytes


class ReleaseMetadataTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.version = {
            "web_version": "5.2.0", "rea_exelearning_version": "4.8.9",
            "exelearning_runtime_version": "4.0.5", "prepared_at": "2026-11-02",
            "web_revision_date": "2026-11-16", "rea_revision": "2026-11-02",
            "download": {"path": "downloads/current.elpx"},
            "sharing_archive": {"path": "downloads/sharing.zip"},
            "source_archive": {"path": "downloads/sources.zip"},
            "english_edition": {
                "language": "en-GB", "base_rea_version": "4.8.9",
                "download": {"path": "en/current.elpx"},
                "sharing_archive": {"path": "en/sharing.zip"},
                "declared_editorial_status": "English private preproduction, 16 November 2026",
            },
        }
        self.tail = "\nUna descripción docente que debe conservarse literalmente.\n\n## Aula\n\nTexto histórico web 4.9.4.\n"
        self.write("README.md", ("# MitoMapa canario · web 4.9.4 · REA 4.8.9\n\nIntroducción propia.\n\n"
                                 "## Edición vigente\n\nEdición web **4.9.4**.\n\n"
                                 "- [Paquete anterior](downloads/old.zip).\n" + self.tail).encode())
        for language, name in (("es", "downloads/current.elpx"), ("en-GB", "en/current.elpx")):
            editorial = {"edition": "4.8.9", "source_revision": "4.8.9", "language": language}
            if language == "en-GB":
                editorial["edition"] = self.version["english_edition"]["declared_editorial_status"]
            self.write(name, zip_bytes({"EDITORIAL_MANIFEST.json": json_bytes(editorial), "content.xml": b"<ode/>"}))
        for name in ("downloads/sharing.zip", "downloads/sources.zip", "en/sharing.zip"):
            self.write(name, zip_bytes({"readme.txt": b"unchanged bytes"}))
        self.write("index.html", b"<html lang='es'></html>")
        self.write("index-en.html", b"<html lang='en'></html>")
        self.write("VERSION.json", json_bytes(self.version))
        self.guide_history = ("<section>Historical web 4.9.4 and REA 4.8.7. "
                              "Mediateca attached edition 4.8.8, announcement 4.8.4. "
                              '<a href="https://example.test/exe/4.0.5/manual">Manual 4.0.5</a></section>')
        for name in ("GUIA_DOCENTE.html", "GUIA_REUTILIZACION.html",
                     "GUIA_DOCENTE-en.html", "GUIA_REUTILIZACION-en.html"):
            guide = ('<html><head><title data-release-version="web">Guide web 4.9.4</title></head><body>'
                     '<p>Web <span data-release-version="web">4.9.4</span>; '
                     'REA <span data-release-version="rea">4.8.8</span>; '
                     'eXeLearning <span data-release-version="runtime">4.0.4</span>.</p>'
                     '<p>Teaching prose must remain unchanged.</p>' + self.guide_history + '</body></html>')
            self.write(name, guide.encode())

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def generate(self):
        for name, data in release_metadata.document_outputs(self.root, self.version).items():
            self.write(name, data)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.root.rglob("*") if p.is_file()}

    def test_documents_use_independent_web_and_rea_revisions_and_preserve_prose(self):
        outputs = release_metadata.document_outputs(self.root, self.version)
        text = outputs["VERSION.txt"].decode()
        self.assertIn("web 5.2.0 · revisión web del 16/11/2026", text)
        self.assertIn("REA editable 4.8.9 · revisión del 02/11/2026", text)
        readme = outputs["README.md"].decode()
        self.assertTrue(readme.startswith("# MitoMapa canario · web 5.2.0 · REA 4.8.9\n"))
        self.assertIn("Introducción propia.", readme)
        self.assertTrue(readme.endswith(self.tail))
        self.assertEqual(json.loads(outputs["version.js"].decode().split("Object.freeze(")[1].split(");")[0]),
                         {"version": "5.2.0", "reaVersion": "4.8.9", "schemaVersion": 1})

    def test_active_guides_use_independent_versions_and_preserve_history_and_prose(self):
        outputs = release_metadata.document_outputs(self.root, self.version)
        for name in ("GUIA_DOCENTE.html", "GUIA_REUTILIZACION.html",
                     "GUIA_DOCENTE-en.html", "GUIA_REUTILIZACION-en.html"):
            with self.subTest(name=name):
                self.assertIn(name, outputs)
                guide = outputs[name].decode()
                self.assertIn('<title data-release-version="web">Guide web 5.2.0</title>', guide)
                self.assertIn('<span data-release-version="web">5.2.0</span>', guide)
                self.assertIn('<span data-release-version="rea">4.8.9</span>', guide)
                self.assertIn('<span data-release-version="runtime">4.0.5</span>', guide)
                self.assertIn('Teaching prose must remain unchanged.', guide)
                self.assertIn(self.guide_history, guide)
        self.generate()
        before = self.snapshot()
        self.assertEqual(outputs, release_metadata.document_outputs(self.root, self.version))
        self.assertEqual(self.snapshot(), before)

    def test_english_guides_follow_their_native_base_independently_of_spanish(self):
        self.version["english_edition"]["base_rea_version"] = "4.8.8"
        english = {"edition": self.version["english_edition"]["declared_editorial_status"],
                   "source_revision": "4.8.8", "language": "en-GB"}
        self.write("en/current.elpx", zip_bytes({"EDITORIAL_MANIFEST.json": json_bytes(english),
                                               "content.xml": b"<ode/>"}))
        outputs = release_metadata.document_outputs(self.root, self.version)
        for name in ("GUIA_DOCENTE.html", "GUIA_REUTILIZACION.html"):
            with self.subTest(name=name):
                self.assertIn('<span data-release-version="rea">4.8.9</span>', outputs[name].decode())
        for name in ("GUIA_DOCENTE-en.html", "GUIA_REUTILIZACION-en.html"):
            with self.subTest(name=name):
                self.assertIn('<span data-release-version="rea">4.8.8</span>', outputs[name].decode())
                self.assertIn('<span data-release-version="web">5.2.0</span>', outputs[name].decode())

    def guide_download_fixture(self, *, package_marker="package"):
        historical = '<a href="downloads/MitoMapa_REA_v4_9_4.zip">Historical package 4.9.4</a>'
        for name in ("GUIA_REUTILIZACION.html", "GUIA_REUTILIZACION-en.html"):
            sharing_marker = "rea" if name.endswith("-en.html") else package_marker
            links = ('<a data-release-download="elpx" href="downloads/old.elpx">REA '
                     '<span data-release-version="rea">4.8.8</span></a>'
                     '<a data-release-download="sharing" href="downloads/old-sharing.zip">Package '
                     '<span data-release-version="' + sharing_marker + '">4.9.4</span> · REA '
                     '<span data-release-version="rea">4.8.8</span></a>'
                     '<a data-release-download="source" href="downloads/old-sources.zip">Sources web '
                     '<span data-release-version="web">4.9.4</span></a>')
            self.write(name, (self.root / name).read_text().replace('</body>', links + historical + '</body>').encode())
        return historical

    def test_current_download_links_and_labels_follow_their_products_not_history(self):
        historical = self.guide_download_fixture()
        self.version["web_version"] = "4.8.8"
        try:
            outputs = release_metadata.document_outputs(self.root, self.version)
        except ValueError as error:
            self.fail("Current package version markers must be supported: " + str(error))
        class Links(HTMLParser):
            def __init__(self, markup):
                super().__init__(); self.links = {}; self.current = None; self.feed(markup)
            def handle_starttag(self, tag, attrs):
                if tag == "a":
                    attrs = dict(attrs); self.current = attrs.get("data-release-download")
                    if self.current: self.links[self.current] = {"href": attrs.get("href"), "text": ""}
            def handle_endtag(self, tag):
                if tag == "a": self.current = None
            def handle_data(self, text):
                if self.current: self.links[self.current]["text"] += text
        for name, prefix in (("GUIA_REUTILIZACION.html", "downloads/"),
                             ("GUIA_REUTILIZACION-en.html", "en/")):
            with self.subTest(name=name):
                guide = outputs[name].decode(); links = Links(guide).links
                self.assertEqual(links["elpx"]["href"], prefix + "current.elpx")
                self.assertEqual(links["sharing"]["href"], prefix + "sharing.zip")
                self.assertEqual(links["source"]["href"], "downloads/sources.zip")
                self.assertEqual(links["elpx"]["text"], "REA 4.8.9")
                self.assertEqual(links["sharing"]["text"], "Package 4.8.9 · REA 4.8.9")
                self.assertEqual(links["source"]["text"], "Sources web 4.8.8")
                self.assertIn(historical, guide)

    def test_check_rejects_stale_current_download_href_without_writing(self):
        self.guide_download_fixture(package_marker="web")
        self.generate()
        for name in ("GUIA_REUTILIZACION.html", "GUIA_REUTILIZACION-en.html"):
            original = (self.root / name).read_bytes()
            self.write(name, original.replace(b'href="downloads/sources.zip"',
                                             b'href="downloads/old-sources.zip"', 1))
            before = self.snapshot()
            with self.assertRaisesRegex(ValueError, name.replace('.', r'\.')):
                release_metadata.check_documents(self.root, self.version)
            self.assertEqual(self.snapshot(), before)
            self.write(name, original)

    def test_check_rejects_stale_guide_values_without_writing(self):
        self.generate()
        for name in ("GUIA_DOCENTE.html", "GUIA_REUTILIZACION.html",
                     "GUIA_DOCENTE-en.html", "GUIA_REUTILIZACION-en.html"):
            original = (self.root / name).read_bytes()
            for marker, stale in ((b'web', b'5.1.0'), (b'rea', b'4.8.8')):
                with self.subTest(name=name, field=marker):
                    # Alter the marked display value, independently of the title.
                    current = b'5.2.0' if marker == b'web' else b'4.8.9'
                    start = b'<span data-release-version="' + marker + b'">'
                    corrupted = original.replace(start + current, start + stale, 1)
                    self.write(name, corrupted)
                    before = self.snapshot()
                    with self.assertRaisesRegex(ValueError, name.replace('.', r'\.')):
                        release_metadata.check_documents(self.root, self.version)
                    self.assertEqual(self.snapshot(), before)
                    self.write(name, original)

    def test_guides_without_english_edition_do_not_generate_english_outputs(self):
        del self.version["english_edition"]
        for name in ("GUIA_DOCENTE-en.html", "GUIA_REUTILIZACION-en.html"):
            (self.root / name).unlink()
        outputs = release_metadata.document_outputs(self.root, self.version)
        self.assertIn("GUIA_DOCENTE.html", outputs)
        self.assertIn("GUIA_REUTILIZACION.html", outputs)
        self.assertNotIn("GUIA_DOCENTE-en.html", outputs)
        self.assertNotIn("GUIA_REUTILIZACION-en.html", outputs)

    def test_update_notice_and_active_change_notes_follow_the_canonical_version(self):
        historical = "REVISIÓN ANTERIOR WEB 4.9.1\nContenido histórico que se conserva.\n"
        self.write("README_ACTUALIZACION.txt", b"MITOMAPA WEB 4.9.4\n" + historical.encode())
        self.version.update(release_notes="CAMBIOS_WEB_5_2_0.md", rea_release_notes="CAMBIOS_REA_4_8_9.md")
        readme = (self.root / "README.md").read_text()
        readme += "\n## Correcciones posteriores a la publicación\n\nVer [web 4.9.4](CAMBIOS_WEB_4_9_4.md) y [REA 4.8.9](CAMBIOS_REA_4_8_9.md).\n"
        self.write("README.md", readme.encode())
        outputs = release_metadata.document_outputs(self.root, self.version)
        notice = outputs["README_ACTUALIZACION.txt"].decode()
        self.assertTrue(notice.startswith("MITOMAPA CANARIO · WEB 5.2.0"))
        self.assertIn(self.version["sharing_archive"]["path"], notice)
        self.assertIn(self.version["source_archive"]["path"], notice)
        self.assertTrue(notice.endswith(historical))
        self.assertIn("Ver [web 5.2.0](CAMBIOS_WEB_5_2_0.md)", outputs["README.md"].decode())
        for name, data in outputs.items():
            self.write(name, data)
        self.assertEqual(outputs, release_metadata.document_outputs(self.root, self.version))
        self.write("README_ACTUALIZACION.txt", b"Stale active edition")
        with self.assertRaisesRegex(ValueError, "README_ACTUALIZACION.txt"):
            release_metadata.check_documents(self.root, self.version)

    def test_two_generations_are_identical_and_do_not_change_archives(self):
        archives = {p: p.read_bytes() for p in self.root.rglob("*") if p.suffix in {".zip", ".elpx"}}
        self.generate()
        first = release_metadata.document_outputs(self.root, self.version)
        self.generate()
        self.assertEqual(release_metadata.document_outputs(self.root, self.version), first)
        self.assertEqual({p: p.read_bytes() for p in archives}, archives)

    def test_check_rejects_each_stale_document_without_writing(self):
        self.generate()
        release_metadata.check_documents(self.root, self.version)
        for name in ("README.md", "VERSION.txt", "version.js", "EDICIONES.md"):
            with self.subTest(name=name):
                original = (self.root / name).read_bytes()
                self.write(name, original.replace(b"5.2.0", b"5.1.0", 1))
                before = self.snapshot()
                with self.assertRaisesRegex(ValueError, name.replace(".", r"\.")):
                    release_metadata.check_documents(self.root, self.version)
                self.assertEqual(self.snapshot(), before)
                self.write(name, original)

    def test_document_generation_and_inventory_do_not_require_git(self):
        with patch("subprocess.run", side_effect=AssertionError("Git must not be needed")):
            outputs = release_metadata.document_outputs(self.root, self.version)
            rows = release_metadata.product_rows(self.root, self.version)
        english = next(row for row in rows if row["product"] == "elpx" and row["language"] == "en-GB")
        self.assertEqual(english["version"], "4.8.9")
        self.assertEqual(english["base_version"], "4.8.9")
        self.assertEqual(english["declared_editorial_status"], self.version["english_edition"]["declared_editorial_status"])
        self.assertEqual(english["sha256"], metadata((self.root / "en/current.elpx").read_bytes())["sha256"])
        self.assertIn("EDICIONES.md", outputs)

    def test_generated_documents_never_embed_generated_zip_digests_or_sizes(self):
        self.version["sharing_archive"].update(metadata((self.root / "downloads/sharing.zip").read_bytes()))
        zip_rows = [row for row in release_metadata.product_rows(self.root, self.version) if row["product"] in {"sharing_zip", "source_zip"}]
        document = release_metadata.document_outputs(self.root, self.version)["EDICIONES.md"].decode()
        for row in zip_rows:
            self.assertNotIn(row["sha256"], document)
        self.assertIn("SHA256SUMS.txt", document)
        self.assertNotIn("sha256", self.version["source_archive"])

    def test_public_observation_is_separate_from_stale_english_editorial_label(self):
        details = metadata((self.root / "en/current.elpx").read_bytes())
        self.version["external_publications"] = {"production": {
            "checked_at_utc": "2026-11-17T22:00:00Z", "reference_commit": "a" * 40,
            "artifacts": [{"path": "en/current.elpx", "http_status": 200, **details}],
        }}
        rows = release_metadata.product_rows(self.root, self.version)
        english = next(row for row in rows if row["product"] == "elpx" and row["language"] == "en-GB")
        self.assertEqual(english["availability"], "public_observed")
        self.assertIn("private preproduction", english["declared_editorial_status"])
        self.assertIn("etiqueta interna", release_metadata.document_outputs(self.root, self.version)["EDICIONES.md"].decode())

    def test_mediateca_announcement_and_download_identity_remain_distinct(self):
        self.version["external_publications"] = {"mediateca": {
            "item_url": "https://example.test/item", "announced_version": "4.8.4",
            "embedded_version": "4.8.8", "download_url": "https://example.test/old.elpx",
            "bytes": 123, "sha256": "b" * 64, "http_status": 200,
            "checked_at_utc": "2026-11-17T22:00:00Z",
        }}
        row = next(row for row in release_metadata.product_rows(self.root, self.version) if row["product"] == "mediateca")
        self.assertEqual(row["version"], "4.8.8")
        self.assertEqual(row["announced_version"], "4.8.4")
        self.assertEqual(row["sha256"], "b" * 64)
        self.assertIn("4.8.4", release_metadata.document_outputs(self.root, self.version)["EDICIONES.md"].decode())

    def test_missing_web_revision_is_not_replaced_by_rea_prepared_date(self):
        del self.version["web_revision_date"]
        text = release_metadata.document_outputs(self.root, self.version)["VERSION.txt"].decode()
        self.assertIn("revisión web no declarada", text)
        self.assertNotIn("revisión web del 02/11/2026", text)

    def test_zip_release_version_can_follow_rea_without_advancing_web(self):
        self.version["web_version"] = "4.8.8"
        rows = release_metadata.product_rows(self.root, self.version)
        sharing = next(row for row in rows if row["product"] == "sharing_zip" and row["language"] == "es")
        self.assertEqual(sharing["version"], "4.8.9")
        self.assertIn("Paquete de la publicación 4.8.9", release_metadata.document_outputs(self.root, self.version)["README.md"].decode())

    def test_changed_public_bytes_are_not_reported_as_matching_observation(self):
        self.version["external_publications"] = {"production": {"artifacts": [
            {"path": "en/current.elpx", "http_status": 200, "sha256": "0" * 64, "bytes": 1}
        ]}}
        row = next(row for row in release_metadata.product_rows(self.root, self.version)
                   if row["product"] == "elpx" and row["language"] == "en-GB")
        self.assertEqual(row["availability"], "public_observation_differs")

    def test_english_authority_rejects_wrong_internal_base_and_hash(self):
        self.version["english_edition"]["base_rea_version"] = "4.8.8"
        with self.assertRaisesRegex(ValueError, "base version"):
            release_metadata.product_rows(self.root, self.version)
        self.version["english_edition"]["base_rea_version"] = "4.8.9"
        self.version["english_edition"]["download"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "English metadata differs"):
            release_metadata.document_outputs(self.root, self.version)

    def test_elpx_input_limit_precedes_any_unbounded_file_read(self):
        path = self.root / "downloads/current.elpx"
        with path.open("wb") as stream:
            stream.truncate(25 * 1024 * 1024 + 1)
        original = Path.read_bytes
        def guarded_read(selected):
            if selected == path:
                raise AssertionError("Unbounded ELPX read")
            return original(selected)
        with patch.object(Path, "read_bytes", guarded_read):
            with self.assertRaisesRegex(ValueError, "compressed.*limit"):
                release_metadata.product_rows(self.root, self.version)

    def test_forged_elpx_member_count_is_rejected_before_directory_expansion(self):
        path = self.root / "downloads/current.elpx"
        payload = bytearray(path.read_bytes())
        eocd = payload.rfind(b"PK\x05\x06")
        struct.pack_into("<HH", payload, eocd + 8, 2001, 2001)
        path.write_bytes(payload)
        with self.assertRaisesRegex(ValueError, "member count.*limit"):
            release_metadata.product_rows(self.root, self.version)


if __name__ == "__main__":
    unittest.main()
