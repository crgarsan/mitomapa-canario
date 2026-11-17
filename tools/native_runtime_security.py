"""Deterministically harden exactly two pinned native iDevice runtimes.

Other libraries and historical files are not modified. Reject an unknown source
instead of silently skipping a transform. Raw project options remain unchanged;
encoding/sanitization is applied where values enter generated HTML.
"""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
MEMBERS = {
    'idevices/progress-report/progress-report.js': ('e4b2f7233af1993feb27e14857f1cef25139871f67b9a33ef1e8b0c221537e72', '$eXeInforme'),
    'idevices/checklist/checklist.js': ('4feca7a3a5a67a396094b543999d1043284b2807dacf745ed683700167411914', '$eXeListaCotejo'),
}
LICENSE_MEMBER = 'libs/mitomapa-native-runtime-LICENSE.txt'


def _replace(source, old, new, count):
    actual = source.count(old)
    if actual != count:
        raise ValueError(f'Native security transform expected {count} occurrences, got {actual}: {old}')
    return source.replace(old, new)


def _helper(root):
    metadata = json.loads((root / 'tools/vendor/DOMPURIFY.json').read_text())
    vendor = (root / metadata['path']).read_bytes()
    license_bytes = (root / metadata['license_path']).read_bytes()
    if hashlib.sha256(vendor).hexdigest() != metadata['sha256']:
        raise ValueError('The pinned DOMPurify bytes have changed')
    if hashlib.sha256(license_bytes).hexdigest() != metadata['license_sha256']:
        raise ValueError('The pinned DOMPurify license has changed')
    locked = json.loads((root / 'package-lock.json').read_text())['packages']['node_modules/dompurify']
    if locked['version'] != metadata['version'] or locked['integrity'] != metadata['npm_integrity']:
        raise ValueError('DOMPurify metadata differs from the dependency lock')
    template = (root / 'tools/native_runtime_security.js').read_text()
    if template.count('/* DOMPURIFY_VENDOR */') != 1:
        raise ValueError('The native sanitizer template marker is missing or duplicated')
    helper = template.replace('/* DOMPURIFY_VENDOR */', vendor.decode() + '\n')
    notice = (
        f"DOMPurify {metadata['version']} — Cure53 and contributors.\n"
        f"Source: {metadata['source']}\n"
        f"SHA-256: {metadata['sha256']}\n"
        'Used under the Apache License 2.0 option of its dual license.\n\n'
    ).encode() + license_bytes
    return helper, notice


def hardened_members(baseline, root=ROOT):
    helper, notice = _helper(root)
    result = {LICENSE_MEMBER: notice}
    for member, (digest, global_name) in MEMBERS.items():
        payload = baseline[member]
        if hashlib.sha256(payload).hexdigest() != digest:
            raise ValueError(f'Unrecognized native runtime source: {member}')
        source = payload.decode()
        safe = global_name + '._mitoSafety'
        if global_name == '$eXeInforme':
            expressions = {
                'pageIdAttr': 1, 'page.title': 1, 'component.odeIdeviceTypeName': 1,
                "component.blockName || ''": 2, 'pTitle': 1, 'odeIdeviceTypeName': 1,
                'blockName': 2, 'surl': 2, 'localmod': 1, 'download': 1,
            }
            for expression, count in expressions.items():
                source = _replace(source, '${' + expression + '}', '${' + safe + '.text(' + expression + ')}', count)
            for expression, attributes in [('pageId', ['data-page-id']), ('component.ideviceID', ['data-idevice-id', 'data-component-id']), ('ideviceID', ['data-idevice-id', 'data-component-id'])]:
                for attribute in attributes:
                    old = attribute + '="${' + expression + '}"'
                    new = attribute + '="${' + safe + '.text(' + expression + ')}"'
                    source = _replace(source, old, new, 1)
            pattern = r'\$\{(\$eXeInforme\.options\.msgs\.[A-Za-z0-9_]+)\}'
            source, count = re.subn(pattern, lambda m: '${' + safe + '.text(' + m[1] + ')}', source)
            if count != 9:
                raise ValueError(f'Unexpected progress message render sites: {count}')
            source = _replace(source, "$('#informeEvalutationNumber').html(", "$('#informeEvalutationNumber').text(", 2)
            source = _replace(source, '$eXeInforme.options.msgs.msgReload ||', safe + ".text($eXeInforme.options.msgs.msgReload || '') ||", 1)
        else:
            for expression, count in {'mOptions.title': 1, 'mOptions.subtitle': 1, 'points': 4}.items():
                source = _replace(source, '${' + expression + '}', '${' + safe + '.text(' + expression + ')}', count)
            for expression, count in {'footer': 1, 'level.item': 4}.items():
                source = _replace(source, '${' + expression + '}', '${' + safe + '.rich(' + expression + ')}', count)
            for variable in ['urlc', 'urll', 'urld']:
                source = _replace(source, 'url(${' + variable + '})', '${' + safe + '.image(' + variable + ')}', 1)
            pattern = r'\$\{(mOptions\.msgs\.[A-Za-z0-9_]+(?: \|\| mOptions\.msgs\.[A-Za-z0-9_]+)?)\}'
            source, count = re.subn(pattern, lambda m: '${' + safe + '.text(' + m[1] + ')}', source)
            if count != 12:
                raise ValueError(f'Unexpected checklist message render sites: {count}')
        source = _replace(source, 'var ' + global_name + ' = {', 'var ' + global_name + ' = {\n    _mitoSafety: ' + helper + ',', 1)
        result[member] = source.encode()
    return result


def apply_runtime_security(files, baseline, root=ROOT):
    files.update(hardened_members(baseline, root))


def verify_runtime_security(files, baseline, root=ROOT):
    for name, expected in hardened_members(baseline, root).items():
        if files.get(name) != expected:
            raise ValueError(f'The hardened native runtime differs from its reviewed transform: {name}')
