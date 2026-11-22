"""Publish the checked Worker version with explicit production credentials."""

import json
import os
import re
import signal
from pathlib import Path
import subprocess
import time
import uuid


# One initial attempt plus eight retries. Pauses total 150 seconds; process
# time shares the 180-second deadline and can shorten this schedule.
VERSION_RETRY_DELAYS = (2, 4, 8, 16, 30, 30, 30, 30)
VERSION_ACTIVATION_TIMEOUT = 180
ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def missing_approved_version(result, version_id, account_id):
    """Recognize only Wrangler's pre-activation lookup of this exact version.

    In the locked Wrangler 4.152.0, this endpoint is read before the deployment
    POST. Never retry an error from /deployments or an ambiguous response.
    """
    stdout = ANSI_ESCAPE.sub('', result.stdout)
    stderr = ANSI_ESCAPE.sub('', result.stderr)
    output = stdout + '\n' + stderr
    expected = f'/accounts/{account_id}/workers/scripts/mitomapa-canario/versions/{version_id}'
    header = re.search(
        r'(?m)^[ \t]*(?:✘[ \t]+)?\[ERROR\][ \t]+A request to the Cloudflare API '
        r'\(([^()\r\n]+)\) failed\.[ \t]*$', stderr)
    note = (re.match(
        r'\s*The requested Worker version could not be found'
        r'(?:, please check the ID being passed and try again)?\.\s+\[code: 100146\]',
        stderr[header.end():]) if header else None)
    return (result.returncode == 1 and header is not None
            and header.group(1) == expected and note is not None
            and output.count('[ERROR]') == 1
            and re.findall(r'A request to the Cloudflare API \(([^()\r\n]+)\) failed\.', output) == [expected]
            and re.findall(r'\[code:\s*([0-9]+)\]', output) == ['100146'])


def activation_attempt(command, environment, timeout):
    # Wrangler's executable is a Node launcher. Own its whole process group so
    # killing the launcher cannot leave its API client running after a timeout.
    with subprocess.Popen(command, env=environment, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True, start_new_session=True) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except BaseException:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
            raise
        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def deploy_approved_version(cli, common, version_id):
    deadline = time.monotonic() + VERSION_ACTIVATION_TIMEOUT
    command = [cli, 'versions', 'deploy', version_id + '@100%', *common,
               '--yes', '--message', os.environ['GITHUB_SHA']]
    environment = {**os.environ, 'WRANGLER_LOG': 'log', 'WRANGLER_WRITE_LOGS': 'false',
                   'WRANGLER_LOG_SANITIZE': 'true', 'WRANGLER_SEND_METRICS': 'false'}
    attempts = len(VERSION_RETRY_DELAYS) + 1
    deadline_message = (f'Worker activation exceeded the {VERSION_ACTIVATION_TIMEOUT}-second '
                        'deadline; no further attempt.')
    print(f'Activating approved Worker version: {version_id}; up to {attempts} attempts '
          f'within a {VERSION_ACTIVATION_TIMEOUT}s activation budget.', flush=True)
    for attempt in range(attempts):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SystemExit(deadline_message)
        try:
            result = activation_attempt(command, environment, remaining)
        except subprocess.TimeoutExpired:
            # A timed-out activation may have reached its POST. Do not repeat it
            # or print the captured output, which can contain sensitive data.
            raise SystemExit('Worker activation timed out; no further attempt.') from None
        if result.returncode == 0:
            print('Activated approved Worker version: ' + version_id, flush=True)
            return
        if not missing_approved_version(result, version_id, os.environ['CLOUDFLARE_ACCOUNT_ID']):
            raise SystemExit('Worker activation failed outside the exact-version 100146 lookup; no retry.')
        if attempt == attempts - 1:
            raise SystemExit(f'Approved Worker version remained unavailable (100146) after {attempts} '
                             f'attempts within the {VERSION_ACTIVATION_TIMEOUT}s activation budget.')
        delay = VERSION_RETRY_DELAYS[attempt]
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SystemExit(deadline_message)
        if remaining <= delay:
            raise SystemExit(f'Insufficient activation budget: retry {attempt + 2}/{attempts} '
                             f'requires a {delay}s pause with {remaining:.1f}s remaining; '
                             'no further attempt.')
        elapsed = VERSION_ACTIVATION_TIMEOUT - remaining
        print(f'Approved version lookup returned 100146 for {version_id}; '
              f'retry {attempt + 2}/{attempts} in {delay}s '
              f'({elapsed:.1f}s elapsed; {remaining:.1f}s left in '
              f'{VERSION_ACTIVATION_TIMEOUT}s budget).', flush=True)
        time.sleep(delay)


def main():
    credentials = ("CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID")
    if any(not os.environ.get(name, "").strip() for name in credentials):
        raise SystemExit("Missing Cloudflare production environment secrets; deployment refused.")

    temporary = Path(os.environ['RUNNER_TEMP'])
    original = json.loads(Path('wrangler.jsonc').read_text())
    if original['name'] != 'mitomapa-canario':
        raise SystemExit('The publication must target the existing MitoMapa Worker.')
    if original['main'] != 'tools/story-video-ranges.mjs':
        raise SystemExit('The only Worker entrypoint is the story video range handler.')
    asset_settings = original['assets']
    if (asset_settings['directory'] != './.deploy' or asset_settings['binding'] != 'ASSETS'
            or asset_settings['html_handling'] != 'auto-trailing-slash'
            or asset_settings['not_found_handling'] != 'none'):
        raise SystemExit('The Worker must use the verified static assets and the existing routing policy.')
    config = {key: original[key] for key in ('name', 'compatibility_date')}
    config['main'] = str(Path('tools/story-video-ranges.mjs').resolve())
    config['assets'] = {key: asset_settings[key] for key in (
        'directory', 'binding', 'html_handling', 'not_found_handling', 'run_worker_first')}
    islands = ('el-hierro', 'fuerteventura', 'gran-canaria', 'la-gomera',
               'la-graciosa', 'la-palma', 'lanzarote', 'tenerife')
    story_videos = [f'/media/{island}/cuento.mp4' for island in islands]
    story_videos += [f'/en/media/{island}/story.mp4' for island in islands]
    if config['assets']['run_worker_first'] != story_videos:
        raise SystemExit('Only the sixteen story MP4 paths may run the Worker before static assets.')
    config['assets']['directory'] = str(Path('.deploy').resolve())
    config_path = temporary / 'mitomapa-story-video.json'
    config_path.write_text(json.dumps(config))
    report_path = temporary / ('mitomapa-upload-' + os.environ['GITHUB_RUN_ID'] + '-' + os.environ['GITHUB_RUN_ATTEMPT'] + '.jsonl')
    if report_path.exists():
        raise SystemExit('The upload report must be new.')
    cli = './node_modules/.bin/wrangler'
    common = ['--config', str(config_path), '--name', 'mitomapa-canario']
    subprocess.run([cli, 'versions', 'upload', *common, '--keep-vars', '--strict', '--message', os.environ['GITHUB_SHA']],
                   env={**os.environ, 'WRANGLER_OUTPUT_FILE_PATH': str(report_path)}, check=True)
    try:
        if not report_path.is_file() or report_path.is_symlink() or report_path.stat().st_size > 1024 * 1024:
            raise ValueError()
        lines = [line for line in report_path.read_text(encoding='utf-8').splitlines() if line.strip()]
        if not lines or len(lines) > 100:
            raise ValueError()
        entries = [json.loads(line) for line in lines]
        if any(not isinstance(entry, dict) for entry in entries):
            raise ValueError()
        reports = [entry for entry in entries if entry.get('type') == 'version-upload']
        if len(reports) != 1:
            raise ValueError()
        report = reports[0]
        version_id = report.get('version_id')
        if (type(report.get('version')) is not int or report['version'] != 1
                or report.get('worker_name') != 'mitomapa-canario'
                or not isinstance(version_id, str) or str(uuid.UUID(version_id)) != version_id):
            raise ValueError()
    except (OSError, ValueError, UnicodeError, RecursionError):
        raise SystemExit('The upload report must identify one valid version of the expected Worker.') from None
    print('Uploaded approved Worker version: ' + version_id, flush=True)
    deploy_approved_version(cli, common, version_id)


if __name__ == "__main__":
    main()
