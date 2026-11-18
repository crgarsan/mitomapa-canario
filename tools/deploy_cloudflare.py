"""Publish the checked Worker version with explicit production credentials."""

import json
import os
from pathlib import Path
import subprocess
import uuid


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
    print('Uploaded approved Worker version: ' + version_id)
    subprocess.run([cli, 'versions', 'deploy', version_id + '@100%', *common, '--yes', '--message', os.environ['GITHUB_SHA']], check=True)


if __name__ == "__main__":
    main()
