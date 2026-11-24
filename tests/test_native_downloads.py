"""External native editions retain their identity and follow the selected language."""

import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import release_metadata


ES_URL = "https://github.com/crgarsan/mitomapa-canario/releases/download/elpx-v5.0.1/MitoMapa_Canario_ES_v5_0_1.elpx"
EN_URL = "https://github.com/crgarsan/mitomapa-canario/releases/download/elpx-v5.0.1/MitoMapa_Canary_Islands_EN_v5_0_1.elpx"


def native_fixture():
    return [
        {"language": "es", "version": "5.0.1", "exelearning_runtime_version": "4.0.6",
         "filename": "MitoMapa_Canario_ES_v5_0_1.elpx", "url": ES_URL,
         "sha256": "a" * 64, "bytes": 469000000},
        {"language": "en-GB", "version": "5.0.1", "exelearning_runtime_version": "4.0.6",
         "filename": "MitoMapa_Canary_Islands_EN_v5_0_1.elpx", "url": EN_URL,
         "sha256": "b" * 64, "bytes": 420000000},
    ]


class NativeDownloadMetadataTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        with ZipFile(self.root / "current.elpx", "w") as archive:
            archive.writestr("content.xml", "<ode/>")
        self.version = {
            "web_version": "4.10.0", "rea_exelearning_version": "4.8.9",
            "exelearning_runtime_version": "4.0.5",
            "download": {"path": "current.elpx"},
            "sharing_archive": {"path": "sharing.zip"},
            "source_archive": {"path": "sources.zip"},
            "native_downloads": native_fixture(),
        }

    def test_external_editions_have_pinned_identity_without_local_binary_reads(self):
        rows = [row for row in release_metadata.product_rows(self.root, self.version)
                if row["product"] == "native_elpx"]
        self.assertEqual(len(rows), 2)
        self.assertEqual([row["language"] for row in rows], ["es", "en-GB"])
        self.assertEqual([row["url"] for row in rows], [ES_URL, EN_URL])
        self.assertEqual([row["bytes"] for row in rows], [469000000, 420000000])
        self.assertEqual([row["sha256"] for row in rows], ["a" * 64, "b" * 64])
        for row in rows:
            self.assertIsNone(row["path"])
            self.assertEqual(row["version"], "5.0.1")
            self.assertEqual(row["exelearning_runtime_version"], "4.0.6")
            self.assertEqual(row["availability"], "external_catalogued")
            self.assertNotIn("public_observation", row)

    def test_catalogue_explains_new_runtime_without_relabelling_existing_elpx(self):
        rows = release_metadata.product_rows(self.root, self.version)
        document = release_metadata._editions(self.version, rows).decode()
        self.assertIn(ES_URL, document)
        self.assertIn(EN_URL, document)
        self.assertIn("a" * 64, document)
        self.assertIn("4.0.6", document)
        local = next(row for row in rows if row["product"] == "elpx")
        self.assertEqual(local["version"], "4.8.9")
        current = release_metadata._current_block(self.version)
        self.assertIn(ES_URL, current)
        self.assertIn(EN_URL, current)
        self.assertIn("4.0.6", current)
        self.assertIn("REA editable vigente · 4.8.9", current)

    def test_legacy_metadata_remains_compatible_when_external_downloads_are_absent(self):
        del self.version["native_downloads"]
        self.assertFalse(any(row["product"] == "native_elpx"
                             for row in release_metadata.product_rows(self.root, self.version)))

    def test_invalid_external_identity_is_rejected(self):
        for field, bad in (
            ("url", ES_URL.replace("https:", "http:")),
            ("url", ES_URL.replace("github.com", "github.com.evil.test")),
            ("url", ES_URL.replace("crgarsan/", "another/")),
            ("url", ES_URL.replace("elpx-v5.0.1", "elpx-v5.0.2")),
            ("url", ES_URL.replace("elpx-v5.0.1", "latest")),
            ("url", ES_URL + "?download=1"),
            ("url", ES_URL + "#fragment"),
            ("url", EN_URL),
            ("filename", "../MitoMapa.elpx"),
            ("filename", "MitoMapa_Canary_Islands_EN_v5_0_1.elpx"),
            ("version", "5.0"),
            ("version", "5.0.2"),
            ("exelearning_runtime_version", "4.0"),
            ("language", "fr"),
            ("sha256", "g" * 64),
            ("sha256", "a" * 63),
            ("sha256", None),
            ("bytes", 0),
            ("bytes", -1),
            ("bytes", True),
            ("bytes", "469000000"),
        ):
            with self.subTest(field=field, value=bad):
                version = copy.deepcopy(self.version)
                version["native_downloads"][0][field] = bad
                with self.assertRaisesRegex(ValueError, "native download"):
                    release_metadata.product_rows(self.root, version)

    def test_incomplete_or_duplicate_language_catalogue_is_rejected(self):
        cases = (None, {}, [], native_fixture()[:1],
                 [native_fixture()[0], native_fixture()[0]], native_fixture() + [native_fixture()[0]])
        for entries in cases:
            with self.subTest(entries=entries):
                version = copy.deepcopy(self.version)
                version["native_downloads"] = entries
                with self.assertRaisesRegex(ValueError, "native download"):
                    release_metadata.product_rows(self.root, version)


class DownloadCards(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.articles = []
        self.card = None
        self.links = {}
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article" and "download-card" in attrs.get("class", "").split():
            self.card = {"attrs": attrs, "text": "", "links": []}
            self.articles.append(self.card)
        elif tag == "a":
            if attrs.get("id"):
                self.links[attrs["id"]] = attrs
            if self.card is not None:
                self.card["links"].append(attrs)

    def handle_data(self, data):
        if self.card is not None:
            self.card["text"] += data

    def handle_endtag(self, tag):
        if tag == "article":
            self.card = None


class NativeDownloadLanguageTests(unittest.TestCase):
    def test_catalogued_files_match_the_visible_downloads(self):
        version = json.loads((ROOT / "VERSION.json").read_text())
        rows = release_metadata.native_download_rows(version)
        self.assertEqual(len(rows), 2)
        for row, filename in zip(rows, ("index.html", "index-en.html")):
            with self.subTest(filename=filename):
                cards = DownloadCards((ROOT / filename).read_text())
                link = cards.links["nativeEditionDownload"]
                self.assertEqual(link["href"], row["url"])
                self.assertEqual(link["download"], row["filename"])

    def test_cards_follow_page_language_and_keep_the_existing_downloads(self):
        for filename, language, url, other_url, legacy in (
            ("index.html", "es", ES_URL, EN_URL, "downloads/MitoMapa_canario_GobCan.elpx"),
            ("index-en.html", "en-GB", EN_URL, ES_URL, "en/downloads/MitoMapa_Canary_Islands_EN.elpx"),
        ):
            with self.subTest(filename=filename):
                cards = DownloadCards((ROOT / filename).read_text())
                self.assertEqual(cards.articles[0]["attrs"].get("id"), "mediatecaResource")
                native = cards.articles[1]
                self.assertEqual(native["attrs"].get("id"), "nativeEditionDownloads")
                self.assertEqual(native["attrs"].get("data-native-language"), language)
                self.assertIn("4.0.6", native["text"])
                self.assertIn("5.0.1", native["text"])
                self.assertEqual(len(native["links"]), 1)
                self.assertEqual(cards.links["nativeEditionDownload"]["href"], url)
                self.assertNotIn(other_url, [link.get("href") for link in native["links"]])
                self.assertTrue(cards.links["currentReaDownload"]["href"].startswith(legacy))
                self.assertIn("currentReaZipDownload", cards.links)


if __name__ == "__main__":
    unittest.main()
