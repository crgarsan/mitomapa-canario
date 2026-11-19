#!/usr/bin/env python3
"""Check pinned deploy-pages startup with real workflow options and no credentials.

The check downloads immutable public GitHub files to a temporary directory, or
uses --bundle-dir for an already downloaded copy. Hashes are checked before Node
runs. Neither invocation can reach a deployment API: the smoke harness blocks
network calls and the empty GitHub environment stops startup at getContext().
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/pages-actions'
EXPECTED_CONTEXT_ERROR = 'workflowRun is undefined. Cannot continue.'


def workflow_runtime(workflow):
    """Read only the selected publishing step's pin and scalar NODE_OPTIONS."""
    steps = re.findall(r'(?ms)^      - (.*?)(?=^      - |\Z)', workflow)
    selected = []
    for step in steps:
        action = re.search(r'(?m)^[ \t]*uses:[ \t]*(actions/deploy-pages@[^ \t\n]+)', step)
        if action:
            selected.append((step, action.group(1)))
    if len(selected) != 1:
        raise ValueError('Expected one deploy-pages step in the backup workflow')
    step, action = selected[0]
    options = re.search(r'(?m)^          NODE_OPTIONS:[ \t]*([^\n]+)$', step)
    value = options.group(1).strip() if options else ''
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        value = value[1:-1]
    value = value.replace('${{ github.workspace }}', str(ROOT))
    if '${{' in value:
        raise ValueError('NODE_OPTIONS contains an unresolved workflow expression')
    if re.search(r'--(?:no-warnings|no-deprecation|disable-warning)(?:[= \t]|$)', value):
        raise ValueError('The Pages runtime must not suppress warnings')
    return action, value


def verify_bundle_file(path, entry):
    payload = path.read_bytes()
    if len(payload) != entry['bytes'] or sha256(payload).hexdigest() != entry['sha256']:
        raise ValueError('Upstream bundle size or SHA-256 mismatch: ' + entry['file'])


def bundle_files(directory, provenance, download):
    """Verify the two exact upstream files, fetching them only when requested."""
    opener = build_opener(ProxyHandler({}))
    for entry in provenance['files']:
        expected_url = ('https://raw.githubusercontent.com/actions/deploy-pages/'
                        + provenance['commit'] + '/dist/' + entry['file'])
        if entry['url'] != expected_url:
            raise ValueError('Unexpected upstream bundle source')
        path = directory / entry['file']
        if download:
            with opener.open(expected_url, timeout=30) as response:
                payload = response.read(entry['bytes'] + 1)
            path.write_bytes(payload)
        verify_bundle_file(path, entry)


def smoke(node, bundle, options):
    # Do not inherit tokens, proxy variables, NODE_OPTIONS or warning controls.
    env = {'PATH': str(Path(node).resolve().parent)}
    if options:
        env['NODE_OPTIONS'] = options
    with tempfile.TemporaryDirectory(prefix='mitomapa-pages-startup-') as directory:
        result = subprocess.run(
            [node, '--trace-deprecation', str(FIXTURES / 'runtime-smoke.js'), str(bundle)],
            cwd=directory, env=env, text=True, capture_output=True, timeout=30, check=False)
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError('Node startup did not return its smoke report') from error
    if (report.get('failure') or {}).get('message') != EXPECTED_CONTEXT_ERROR or result.returncode != 1:
        raise ValueError('The action did not stop at the expected empty-context boundary')
    if report.get('networkAttempts'):
        raise ValueError('The action attempted a network call during startup')
    codes = [warning.get('code') for warning in report.get('warnings', [])]
    if 'MITOMAPA_SMOKE' not in codes or 'MITOMAPA_SMOKE' not in result.stderr:
        raise ValueError('The independent warning probe was suppressed')
    return report, codes.count('DEP0040'), result.stderr


def check(node, directory, provenance):
    version = subprocess.run([node, '--version'], env={}, text=True, capture_output=True,
                             timeout=10, check=True).stdout.strip()
    if not re.fullmatch(r'v24\.\d+\.\d+', version):
        raise ValueError('The Pages runtime smoke check requires Node.js 24')
    action, options = workflow_runtime((ROOT / '.github/workflows/deploy-backup.yml').read_text())
    if action != 'actions/deploy-pages@' + provenance['commit']:
        raise ValueError('Retain verified upstream bundle provenance for the selected action pin')
    bundle = directory / 'index.js'
    control, control_count, control_stderr = smoke(node, bundle, '')
    configured, configured_count, configured_stderr = smoke(node, bundle, options)
    control_versions = {item['version'] for item in control['punycodeLoads']}
    configured_versions = {item['version'] for item in configured['punycodeLoads']}
    if control_count < 1 or 'DEP0040' not in control_stderr or control_versions != {'2.1.0'}:
        raise ValueError('The unmodified action control did not reproduce core punycode DEP0040')
    if configured_count or 'DEP0040' in configured_stderr or configured_versions != {'2.3.1'}:
        raise ValueError('Configured Pages startup still loads core punycode or emits DEP0040')
    return {
        'ok': True, 'action': 'actions/deploy-pages', 'commit': provenance['commit'],
        'node': version, 'control_dep0040_count': control_count,
        'configured_dep0040_count': configured_count,
        'control_punycode_version': '2.1.0', 'configured_punycode_version': '2.3.1',
        'network_attempts': 0, 'warning_probe_visible': True,
        'startup_failure': EXPECTED_CONTEXT_ERROR,
        'scope': 'Startup only; no credentials, artifact lookup or deployment.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', required=True,
                        help='Verify only; do not change repository files')
    parser.add_argument('--bundle-dir', type=Path,
                        help='Use an existing directory with the two pinned dist files; no download')
    parser.add_argument('--node', default=shutil.which('node'),
                        help='Node.js 24 executable (default: node on PATH)')
    args = parser.parse_args()
    try:
        if not args.node:
            raise ValueError('Node.js 24 is required; select its executable with --node')
        node = shutil.which(args.node) or args.node
        provenance = json.loads((FIXTURES / 'runtime-provenance.json').read_text())
        if args.bundle_dir:
            directory = args.bundle_dir.resolve()
            bundle_files(directory, provenance, download=False)
            report = check(node, directory, provenance)
        else:
            with tempfile.TemporaryDirectory(prefix='mitomapa-pages-bundle-') as temporary:
                directory = Path(temporary)
                bundle_files(directory, provenance, download=True)
                report = check(node, directory, provenance)
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, ValueError, URLError, subprocess.SubprocessError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
