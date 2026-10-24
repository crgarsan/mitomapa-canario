"""Guard the dependency and workflow boundaries before deployment credentials."""

import base64
import binascii
import copy
import json
import hashlib
from fnmatch import fnmatchcase
from html.parser import HTMLParser
import struct
from pathlib import Path, PurePosixPath
import re
import unittest
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent.parent
EXACT_VERSION = re.compile(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?")


def lock_errors(manifest, lock):
    """Check every tarball and every required/optional edge, not just Wrangler."""
    errors = []
    packages = lock.get("packages", {})
    if lock.get("lockfileVersion") != 3 or "" not in packages:
        return ["Missing npm v3 package graph"]
    root = packages[""]
    if root.get("devDependencies") != manifest.get("devDependencies"):
        errors.append("Manifest and lock root dependencies differ")
    version = manifest.get("devDependencies", {}).get("wrangler", "")
    if not EXACT_VERSION.fullmatch(version):
        errors.append("Wrangler must have an exact version")
    if packages.get("node_modules/wrangler", {}).get("version") != version:
        errors.append("Wrangler lock version differs from manifest")

    for name, package in packages.items():
        if name:
            if not EXACT_VERSION.fullmatch(package.get("version", "")):
                errors.append(f"Unpinned package: {name}")
            url = urlsplit(package.get("resolved", ""))
            if (url.scheme != "https" or url.netloc != "registry.npmjs.org"
                    or not url.path.endswith(".tgz") or url.query or url.fragment):
                errors.append(f"Unexpected package origin: {name}")
            algorithm, _, digest = package.get("integrity", "").partition("-")
            try:
                valid_integrity = algorithm == "sha512" and len(
                    base64.b64decode(digest, validate=True)
                ) == 64
            except (ValueError, binascii.Error):
                valid_integrity = False
            if not valid_integrity:
                errors.append(f"Missing or invalid SHA-512 integrity: {name}")

        # npm resolves a dependency from the package's nearest node_modules
        # directory, then from its ancestors. Optional platform packages must
        # also be retained in the lock even when this runner does not install them.
        dependencies = {
            **package.get("dependencies", {}),
            **package.get("optionalDependencies", {}),
        }
        dependencies.update({
            dependency: version
            for dependency, version in package.get("peerDependencies", {}).items()
            if not package.get("peerDependenciesMeta", {}).get(dependency, {}).get("optional")
        })
        if not name:
            dependencies.update(package.get("devDependencies", {}))
        for dependency in dependencies:
            directory = PurePosixPath(name)
            while True:
                candidate = (directory / "node_modules" / dependency).as_posix()
                if candidate in packages:
                    break
                if directory == PurePosixPath("."):
                    errors.append(f"Missing graph edge: {name} -> {dependency}")
                    break
                directory = directory.parent
    return errors


class DeployPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = (ROOT / ".github/workflows/deploy-cloudflare.yml").read_text()
        cls.manifest = json.loads((ROOT / "package.json").read_text())
        cls.lock = json.loads((ROOT / "package-lock.json").read_text())
        cls.steps = re.findall(r"(?ms)^      - (.*?)(?=^      - |\Z)", cls.workflow)

    def test_actions_use_full_commit_ids(self):
        actions = re.findall(r"^\s*- uses: (\S+)(.*)$", self.workflow, re.MULTILINE)
        self.assertEqual(len(actions), 4)
        self.assertEqual({action.split("@")[0] for action, _ in actions},
                         {"actions/checkout", "actions/setup-node"})
        for action, comment in actions:
            with self.subTest(action=action):
                self.assertRegex(action, r"^actions/[a-z-]+@[0-9a-f]{40}$")
                self.assertRegex(comment, r"^\s+# (?:v\d+\.\d+\.\d+|v\d+ \(backport #\d+\))\s*$")

    def test_manifest_and_complete_lock_have_integrity(self):
        self.assertTrue(self.manifest.get("private"))
        self.assertEqual(self.manifest.get("engines", {}).get("node"), ">=22")
        self.assertEqual(lock_errors(self.manifest, self.lock), [])

    def test_lock_policy_rejects_tampered_transitive_entries(self):
        dependency = next(iter(self.lock["packages"]["node_modules/wrangler"]["dependencies"]))
        dependency_path = "node_modules/" + dependency
        for mutation in ("integrity", "origin", "missing"):
            with self.subTest(mutation=mutation):
                damaged = copy.deepcopy(self.lock)
                package = damaged["packages"][dependency_path]
                if mutation == "integrity":
                    del package["integrity"]
                elif mutation == "origin":
                    package["resolved"] = "https://example.com/package.tgz"
                else:
                    del damaged["packages"][dependency_path]
                self.assertTrue(lock_errors(self.manifest, damaged))

    def test_install_and_deploy_cannot_fetch_an_unlocked_cli(self):
        self.assertNotRegex(self.workflow, r"\b(?:npx|npm\s+(?:install|i|exec))\b")
        install = next(step for step in self.steps if step.startswith("name: Install Wrangler\n"))
        deploy = next(step for step in self.steps if step.startswith("name: Deploy existing Worker\n"))
        self.assertIn("        run: npm ci --ignore-scripts --no-audit --no-fund\n", install)
        self.assertIn("          ./node_modules/.bin/wrangler deploy --config wrangler.jsonc\n", deploy)
        self.assertLess(deploy.index("python3 tools/check_custom_domain.py"),
                        deploy.index("./node_modules/.bin/wrangler deploy"))
        self.assertLess(self.steps.index(install), self.steps.index(deploy))
        self.assertIn("      WRANGLER_SEND_METRICS: 'false'\n", self.workflow)

    def test_checks_run_before_credentials(self):
        deploy_index = next(i for i, step in enumerate(self.steps)
                            if "secrets.CLOUDFLARE_API_TOKEN" in step)
        prior_steps = "\n".join(self.steps[:deploy_index])
        self.assertNotIn("secrets.", prior_steps)
        self.assertIn("python3 -m unittest discover -s tests -p 'test_deploy_policy.py'", prior_steps)
        self.assertIn("node --test tests/drawing-import.test.js", prior_steps)
        self.assertIn("python3 tools/prepare_deploy.py", prior_steps)
        self.assertIn("python3 tools/update_release.py --check", prior_steps)
        self.assertIn("python3 tools/sync_current_elpx.py --check", prior_steps)
        self.assertIn("test_experience_browser.py", prior_steps)
        self.assertEqual(self.workflow.count("secrets."), 2)
        self.assertIn("CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}", self.steps[deploy_index])
        self.assertIn("CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}", self.steps[deploy_index])

    def test_deployment_contracts_remain_restricted(self):
        self.assertIn("  pull_request:\n", self.workflow)
        self.assertIn("  push:\n    branches: [main]\n  workflow_dispatch:\n", self.workflow)
        self.assertIn("    if: github.ref == 'refs/heads/main' && github.repository == 'crgarsan/mitomapa-canario'\n", self.workflow)
        self.assertIn("    environment: production\n", self.workflow)
        permissions = re.search(r"^    permissions:\n((?:      .+\n)+)",
                                self.workflow, re.MULTILINE)
        self.assertIsNotNone(permissions)
        self.assertEqual(permissions.group(1), "      contents: read\n")
        self.assertIn("          persist-credentials: false\n", self.workflow)
        self.assertIn("          node-version: '22'\n", self.workflow)
        self.assertIn("  cancel-in-progress: false\n", self.workflow)
        self.assertIn("  group: mitomapa-cloudflare-${{ github.ref }}\n", self.workflow)

    def test_validation_is_separate_and_cannot_access_production(self):
        validation = self.workflow.split("  validate:\n", 1)[1].split("  deploy:\n", 1)[0]
        deployment = self.workflow.split("  deploy:\n", 1)[1]
        self.assertNotIn("secrets.", validation)
        self.assertNotIn("environment:", validation)
        self.assertIn("    needs: validate\n", deployment)
        self.assertIn("    environment: production\n", deployment)
        self.assertNotIn("pull_request_target", self.workflow)
        requirements = (ROOT / "requirements-browser-tests.txt").read_text()
        for line in requirements.splitlines():
            if line and not line.startswith("#"):
                self.assertRegex(line, r"^[A-Za-z][A-Za-z0-9_-]*==\d+\.\d+\.\d+$")

    def test_share_preview_is_versioned_and_matches_the_actual_png(self):
        class MetaTags(HTMLParser):
            def __init__(self):
                super().__init__()
                self.values = {}
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == "meta":
                    self.values[attrs.get("property", attrs.get("name"))] = attrs.get("content")
        parser = MetaTags()
        parser.feed((ROOT / "index.html").read_text())
        meta = parser.values
        image = urlsplit(meta["og:image"])
        self.assertEqual(image.scheme, "https")
        self.assertEqual(image.netloc, urlsplit(meta["og:url"]).netloc)
        self.assertRegex(image.path, r"^/og-image-v[0-9]+-[0-9]+-[0-9]+\.png$")
        self.assertEqual(meta["twitter:image"], meta["og:image"])
        self.assertEqual(meta["og:image:secure_url"], meta["og:image"])
        self.assertEqual(meta["og:image:type"], "image/png")
        payload = (ROOT / image.path.lstrip("/")).read_bytes()
        self.assertEqual(payload[:8], b"\x89PNG\r\n\x1a\n")
        dimensions = struct.unpack(">II", payload[16:24])
        self.assertEqual(dimensions, (int(meta["og:image:width"]), int(meta["og:image:height"])))
        self.assertEqual(dimensions, (1200, 630))
        self.assertLess(len(payload), 300 * 1024)
        self.assertEqual(payload, (ROOT / "og-image.png").read_bytes())
        public_entry = hashlib.sha256(payload).hexdigest() + "  " + image.path.lstrip("/")
        self.assertTrue(public_entry in (ROOT / "SHA256SUMS.txt").read_text().splitlines(),
                        "The versioned preview must be in the verified public asset inventory")
        self.assertIn("piezas", meta["og:image:alt"].lower())

    def test_audio_loading_remains_limited_to_the_resource_origin(self):
        headers = (ROOT / "_headers").read_text()
        policy = next(line for line in headers.splitlines() if "Content-Security-Policy:" in line)
        directives = dict(part.strip().split(" ", 1) for part in policy.split(":", 1)[1].split(";") if part.strip())
        self.assertEqual(directives["connect-src"], "'self'")
        self.assertEqual(directives["script-src"], "'self'")
        self.assertEqual(directives["media-src"], "'self' data: blob:")

    def test_current_editable_download_has_one_attachment_header_and_its_native_filename(self):
        version = json.loads((ROOT / "VERSION.json").read_text())
        download = "/" + version["download"]["path"]
        headers = (ROOT / "_headers").read_text()
        rules = re.findall(r"(?m)^(\S[^\n]*)\n((?:[ \t]+[^\n]*\n?)+)", headers)
        exact = [block for route, block in rules if route == download]
        self.assertEqual(len(exact), 1, "The current ELPX needs one exact download rule")
        matching = [block for route, block in rules if fnmatchcase(download, route)]
        values = [(name.strip().lower(), value.strip()) for block in matching
                  for name, _, value in (line.partition(":") for line in block.splitlines())]
        filename = "MitoMapa_canario_" + version["rea_exelearning_version"].replace(".", "_") + ".elpx"
        self.assertEqual([value for name, value in values if name == "content-type"],
                         ["application/octet-stream"])
        self.assertEqual([value for name, value in values if name == "content-disposition"],
                         ['attachment; filename="' + filename + '"'])
        global_blocks = [block for route, block in rules if route == "/*"]
        global_headers = {line.partition(":")[0].strip().lower()
                          for block in global_blocks for line in block.splitlines()}
        for protection in ("content-security-policy", "permissions-policy", "referrer-policy",
                           "x-content-type-options", "x-frame-options", "cross-origin-resource-policy"):
            with self.subTest(protection=protection):
                self.assertIn(protection, global_headers)


if __name__ == "__main__":
    unittest.main()
