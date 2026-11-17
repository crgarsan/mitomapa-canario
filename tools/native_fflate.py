"""Replace only the reviewed native fflate member with a pinned upstream build."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEMBER = 'libs/fflate/fflate.umd.js'
LICENSE_MEMBER = 'libs/fflate/LICENSE.txt'
SOURCE_SHA256 = 'c3b34f2e9f5e74d4d7d64e01cac7a0c01954c6c406414d42185c7b53d6875ddf'
PIN = {
    'version': '0.8.3',
    'path': 'tools/vendor/fflate-0.8.3.umd.js',
    'sha256': '462ef8041fc970e3615a20a9dd2b2e3047a073b2da729ef4f02b634bba8b7b83',
    'license_path': 'tools/vendor/fflate-LICENSE.txt',
    'license_sha256': '0a1df3a083d0c010560aa342e87959c8c1070e6fd54545741f083f22d0c8b551',
    'npm_integrity': 'sha512-tbZNuJrLwGUp3zshBtdy4W+ORxZuIh8a5ilyIEQDC5rY1f3U20JMry0Ll3WBzU58EZKsEuJFXhb5gwv8CsPvgA==',
    'source': 'https://registry.npmjs.org/fflate/-/fflate-0.8.3.tgz',
    'license': 'MIT',
}


def upgraded_members(baseline, root=ROOT):
    if hashlib.sha256(baseline.get(MEMBER, b'')).hexdigest() != SOURCE_SHA256:
        raise ValueError('Unrecognized native fflate source')
    metadata = json.loads((root / 'tools/vendor/FFLATE.json').read_text())
    if any(metadata.get(key) != value for key, value in PIN.items()):
        raise ValueError('The fflate metadata differs from its reviewed pin')
    locked = json.loads((root / 'package-lock.json').read_text())['packages']['node_modules/fflate']
    declared = json.loads((root / 'package.json').read_text())['devDependencies']['fflate']
    if declared != PIN['version'] or locked['version'] != PIN['version'] or locked['integrity'] != PIN['npm_integrity']:
        raise ValueError('fflate metadata differs from the dependency lock')
    result = {}
    for member, path_key, hash_key in ((MEMBER, 'path', 'sha256'), (LICENSE_MEMBER, 'license_path', 'license_sha256')):
        payload = (root / PIN[path_key]).read_bytes()
        if hashlib.sha256(payload).hexdigest() != PIN[hash_key]:
            raise ValueError(f'The pinned fflate bytes have changed: {member}')
        result[member] = payload
    return result


def apply_fflate_upgrade(files, baseline, root=ROOT):
    # Validate every input before touching the destination dictionary.
    files.update(upgraded_members(baseline, root))


def verify_fflate_upgrade(files, baseline, root=ROOT):
    for name, expected in upgraded_members(baseline, root).items():
        if files.get(name) != expected:
            raise ValueError(f'The native fflate member differs from its reviewed pin: {name}')
