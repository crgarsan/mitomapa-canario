"""Protect existing Cloudflare domains and DNS before a noninteractive deploy."""

import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "check_custom_domain.py"


class CustomDomainPreflightTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), "The deployment needs a domain preflight")
        spec = importlib.util.spec_from_file_location("check_custom_domain", SCRIPT)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def preview(self, **changes):
        return {"added": [], "removed": [], "updated": [], "conflicting": [], **changes}

    def test_allows_adding_only_the_requested_domain(self):
        self.module.check_changeset(self.preview(added=[{"hostname": "mitomapacanario.org"}]))

    def test_allows_an_already_matching_domain(self):
        self.module.check_changeset(self.preview(updated=[{
            "hostname": "mitomapacanario.org", "modified": False
        }]))

    def test_rejects_removing_any_existing_domain(self):
        with self.assertRaises(self.module.PreflightError):
            self.module.check_changeset(self.preview(removed=[{"hostname": "existing.example"}]))

    def test_rejects_replacing_an_existing_dns_record(self):
        with self.assertRaises(self.module.PreflightError):
            self.module.check_changeset(self.preview(conflicting=[{"hostname": "mitomapacanario.org"}]))

    def test_rejects_reassigning_or_modifying_an_existing_binding(self):
        for update in [{"hostname": "mitomapacanario.org", "modified": True},
                       {"hostname": "mitomapacanario.org"}]:
            with self.subTest(update=update), self.assertRaises(self.module.PreflightError):
                self.module.check_changeset(self.preview(updated=[update]))

    def test_rejects_an_unrequested_hostname(self):
        with self.assertRaises(self.module.PreflightError):
            self.module.check_changeset(self.preview(added=[{"hostname": "other.example"}]))

    def test_rejects_incomplete_or_malformed_preview(self):
        for preview in [None, {}, {"added": []}, self.preview(removed=None),
                        self.preview(added=[{}]), self.preview(added=["mitomapacanario.org"])]:
            with self.subTest(preview=preview), self.assertRaises(self.module.PreflightError):
                self.module.check_changeset(preview)


if __name__ == "__main__":
    unittest.main()
