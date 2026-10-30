"""Exercise release packaging boundaries with small, independent fixtures."""

from io import BytesIO
import csv
from html.parser import HTMLParser
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
from update_release import DOCUMENTS, check_download_button, check_elpx, check_release, release_paths, sharing_document, update_release


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
<a href="downloads/Pauta_de_revision_MitoMapa.html">Pauta</a>
<a href="index.html#recursos">Web</a>
<a href="downloads/MitoMapa_canario_GobCan.elpx">Editar</a>''')
        update_release(self.root)
        sharing = read_zip((self.root / self.version["sharing_archive"]["path"]).read_bytes())
        guide = sharing["documentacion/GUIA_DOCENTE.html"].decode()
        self.assertIn('href="styles.css"', guide)
        self.assertIn("documentacion/styles.css", sharing)
        self.assertIn("documentacion/docente.css", sharing)
        self.assertIn("documentacion/downloads/Pauta_de_revision_MitoMapa.html", set(sharing))
        self.assertIn('href="downloads/Pauta_de_revision_MitoMapa.html"', guide)
        self.assertIn('href="https://mitomapacanario.org/index.html#recursos"', guide)
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

    def test_editable_revision_can_advance_without_changing_the_web_edition(self):
        version = {**self.version, "release_version": "4.6.1", "rea_exelearning_version": "4.6.1",
                   "sharing_archive": {"path": "downloads/MitoMapa_REA_v4_6_1.zip"},
                   "source_archive": {"path": "downloads/MitoMapa_fuentes_web_v4_6_1.zip"}}
        paths = release_paths(version)
        self.assertEqual(version["web_version"], "4.6.0")
        self.assertEqual(paths["sharing_archive"], "downloads/MitoMapa_REA_v4_6_1.zip")
        version["rea_exelearning_version"] = "4.6.2"
        with self.assertRaisesRegex(ValueError, "differs from its delivery"):
            release_paths(version)

    def test_web_revision_can_advance_without_changing_the_editable_edition(self):
        version = {**self.version, "release_version": "4.6.1", "web_version": "4.6.1",
                   "sharing_archive": {"path": "downloads/MitoMapa_REA_v4_6_1.zip"},
                   "source_archive": {"path": "downloads/MitoMapa_fuentes_web_v4_6_1.zip"}}
        try:
            paths = release_paths(version)
        except ValueError as error:
            self.fail(f"A web-only revision must retain the existing editable: {error}")
        self.assertEqual(version["rea_exelearning_version"], "4.6.0")
        self.assertEqual(paths["source_archive"], "downloads/MitoMapa_fuentes_web_v4_6_1.zip")

    def test_delivery_uses_the_numeric_maximum_of_web_and_editable_versions(self):
        version = {**self.version, "release_version": "4.10.0", "web_version": "4.10.0",
                   "rea_exelearning_version": "4.9.9",
                   "sharing_archive": {"path": "downloads/MitoMapa_REA_v4_10_0.zip"},
                   "source_archive": {"path": "downloads/MitoMapa_fuentes_web_v4_10_0.zip"}}
        try:
            paths = release_paths(version)
        except ValueError as error:
            self.fail(f"The numeric latest edition must define the delivery: {error}")
        self.assertEqual(paths["sharing_archive"], "downloads/MitoMapa_REA_v4_10_0.zip")

    def test_delivery_rejects_a_version_behind_or_ahead_of_both_editions(self):
        for release in ("4.6.0", "4.6.2"):
            version = {**self.version, "release_version": release, "web_version": "4.6.1",
                       "sharing_archive": {"path": f"downloads/MitoMapa_REA_v{release.replace('.', '_')}.zip"},
                       "source_archive": {"path": f"downloads/MitoMapa_fuentes_web_v{release.replace('.', '_')}.zip"}}
            with self.subTest(release=release), self.assertRaisesRegex(ValueError, "differs from its delivery"):
                release_paths(version)

    def test_delivery_rejects_malformed_edition_metadata_and_paths(self):
        for key in ("release_version", "web_version", "rea_exelearning_version"):
            for malformed in ("4.6", "4.6.0-beta", "four.6.0"):
                version = {**self.version, "release_version": "4.6.0", key: malformed}
                with self.subTest(field=key, value=malformed), self.assertRaises(ValueError):
                    release_paths(version)
        version = {**self.version, "release_version": "4.6.1", "web_version": "4.6.1",
                   "sharing_archive": {"path": "downloads/MitoMapa_REA_v4_6_1.zip"},
                   "source_archive": {"path": "downloads/MitoMapa_fuentes_web_v4_6_1.zip"}}
        for key in ("sharing_archive", "source_archive"):
            invalid = {**version, key: self.version[key]}
            with self.subTest(path=key), self.assertRaisesRegex(ValueError, key):
                release_paths(invalid)

    def test_source_archive_includes_dependabot_configuration_when_present(self):
        config = b"version: 2\nupdates: []\n"
        self.write(".github/dependabot.yml", config)
        update_release(self.root)
        sources = read_zip((self.root / self.version["source_archive"]["path"]).read_bytes())
        self.assertEqual(sources.get(".github/dependabot.yml"), config)

    def test_source_archive_includes_pinned_native_builder_inputs(self):
        inputs = {
            "tools/vendor/FFLATE.json": b'{"version":"0.8.3"}',
            "tools/vendor/fflate-0.8.3.umd.js": b"upstream fflate fixture",
            "tools/vendor/fflate-LICENSE.txt": b"MIT fixture",
            "tools/vendor/DOMPURIFY.json": b'{"version":"3.4.17"}',
            "tools/vendor/dompurify-3.4.17.min.js": b"upstream sanitizer fixture",
            "tools/native_runtime_security.js": b"native sanitizer template fixture",
        }
        for name, payload in inputs.items():
            self.write(name, payload)
        update_release(self.root)
        sources = read_zip((self.root / self.version["source_archive"]["path"]).read_bytes())
        for name, payload in inputs.items():
            with self.subTest(input=name):
                self.assertEqual(sources.get(name), payload)

    def test_download_advertises_the_actual_editable_version_and_revision(self):
        version = {**self.version, "download": {**self.version["download"], "sha256": "a" * 64}}
        markup = ('<a id="currentReaDownload" data-rea-version="4.6.0" '
                  'href="downloads/MitoMapa_canario_GobCan.elpx?revision=aaaaaaaaaaaa" '
                  'download="MitoMapa_canario_4_6_0.elpx">Descargar REA 4.6.0</a>')
        check_download_button(markup, version)
        for wrong in (markup.replace('Descargar REA 4.6.0', 'Descargar REA 4.5.1'),
                      markup.replace('data-rea-version="4.6.0"', 'data-rea-version="4.5.1"'),
                      markup.replace('4_6_0.elpx', '4_5_1.elpx'),
                      markup.replace('revision=aaaaaaaaaaaa', 'revision=bbbbbbbbbbbb'),
                      markup.replace('_GobCan.elpx?', '_antiguo.elpx?'), '', markup * 2):
            with self.subTest(markup=wrong), self.assertRaises(ValueError):
                check_download_button(wrong, version)

    def test_shared_classroom_documents_keep_their_relative_companion_links_local(self):
        documents = {"downloads/Cuaderno_de_ruta_MitoMapa.html", "downloads/Pauta_de_revision_MitoMapa.html", "downloads/Pauta_de_revision_MitoMapa.csv"}
        markup = ('<a href="Pauta_de_revision_MitoMapa.html#revision">Pauta</a>'
                  '<a href="Pauta_de_revision_MitoMapa.csv">CSV</a>'
                  '<a href="../downloads/MitoMapa_canario_GobCan.elpx">ELPX</a>'
                  '<a href="../index.html#recursos">Web</a>')
        actual = sharing_document(markup.encode(), "downloads/Cuaderno_de_ruta_MitoMapa.html", documents, self.version).decode()
        self.assertIn('href="Pauta_de_revision_MitoMapa.html#revision"', actual)
        self.assertIn('href="Pauta_de_revision_MitoMapa.csv"', actual)
        self.assertIn('href="../../MitoMapa_canario_GobCan.elpx"', actual)
        self.assertIn('href="https://mitomapacanario.org/index.html#recursos"', actual)

    @staticmethod
    def raw_zip(entries):
        output = BytesIO()
        with ZipFile(output, "w") as archive:
            for name, payload in entries:
                archive.writestr(name, payload)
        return output.getvalue()


class CurrentClassroomMaterialsTests(unittest.TestCase):
    class Document(HTMLParser):
        def __init__(self, markup):
            super().__init__(convert_charrefs=True)
            self.links = []
            self.words = []
            self.feed(markup)
        def handle_starttag(self, tag, attrs):
            if tag == "a":
                self.links.append(dict(attrs).get("href", ""))
        def handle_data(self, data):
            self.words.append(data)

    def test_current_site_and_guides_link_the_current_classroom_materials(self):
        current = {"downloads/Cuaderno_de_ruta_MitoMapa.html", "downloads/Pauta_de_revision_MitoMapa.html", "downloads/Pauta_de_revision_MitoMapa.csv"}
        legacy = {"downloads/Cuaderno_de_ruta_MitoMapa_web_4_0.html", "downloads/Rubrica_lectura_MitoMapa_4_0.html", "downloads/Rubrica_MitoMapa_4_0.csv"}
        self.assertTrue(current <= set(DOCUMENTS), "The current shared package still uses the historical classroom files")
        self.assertFalse(legacy & set(DOCUMENTS))
        index = (ROOT / "index.html").read_text()
        self.assertNotIn("Otras versiones 4.4.0", index)
        for name in ("index.html", "GUIA_DOCENTE.html", "GUIA_DOCENTE_GOBCAN.html", "GUIA_REUTILIZACION.html"):
            with self.subTest(document=name):
                links = self.Document((ROOT / name).read_text()).links
                self.assertFalse(legacy & set(links), "A current guide still links a historical classroom sheet")
                self.assertFalse(any("_Esencial.elpx" in link or "_Intermedio.elpx" in link for link in links))
        self.assertTrue(current <= set(self.Document(index).links))
        for name in current:
            self.assertTrue((ROOT / name).is_file(), name)
        version = json.loads((ROOT / "VERSION.json").read_text())
        for key, prefix in (("sharing_archive", "documentacion/"), ("source_archive", "")):
            with ZipFile(ROOT / version[key]["path"]) as archive:
                names = set(archive.namelist())
                self.assertTrue({prefix + name for name in current} <= names)
                self.assertFalse({prefix + name for name in legacy} & names)

    def test_editable_pauta_contains_the_same_six_questions_as_the_printable_sheet(self):
        sheet = self.Document((ROOT / "downloads/Pauta_de_revision_MitoMapa.html").read_text())
        text = " ".join(" ".join(sheet.words).split())
        with (ROOT / "downloads/Pauta_de_revision_MitoMapa.csv").open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(reader.fieldnames, ["Aspecto", "Pregunta orientadora", "Evidencia", "Avance", "Siguiente paso", "Procede"])
            rows = list(reader)
        self.assertEqual(len(rows), 6)
        self.assertEqual(len({row["Aspecto"] for row in rows}), 6)
        for row in rows:
            self.assertIn(row["Aspecto"], text)
            self.assertTrue(row["Pregunta orientadora"])
            self.assertIn(row["Pregunta orientadora"], text)
            self.assertTrue(all(row[column] == "" for column in ["Evidencia", "Avance", "Siguiente paso", "Procede"]))
        self.assertIn("https://creativecommons.org/licenses/by-sa/4.0/deed.es", sheet.links)


if __name__ == "__main__":
    unittest.main()
