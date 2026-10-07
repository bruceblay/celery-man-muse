#!/usr/bin/env python3
"""Install the character pack into an existing Muse Gadget SDK checkout."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
REVISION = '1b56662588c0ea00bdee24b9bcd1835e12848e9a'
RUNTIME = ['muse_pixel.c', 'characters.h', 'muse_default.c', 'muse_default.h'] + [
    f'{name}/sprites.h' for name in ('tayne', 'celery-man', 'oyster')
]


def install(sdk, check=False):
    sdk = sdk.resolve()
    component = sdk / 'esp32/components/muse'
    if not (component / 'muse_pixel.h').is_file():
        raise RuntimeError('Pass the Muse Gadget SDK repository root (the directory containing esp32).')
    git = ['git', '-C', str(sdk)]
    revision = subprocess.check_output(git + ['rev-parse', 'HEAD'], text=True).strip()
    if revision != REVISION:
        raise RuntimeError(f'Use the supported SDK revision {REVISION}; found {revision}.')
    patch = str(ROOT / 'patches/muse-character-menu.patch')
    def applicable(reverse=False, path=patch):
        args = git + ['apply', '--check'] + (['--reverse'] if reverse else []) + [path]
        return subprocess.run(args, capture_output=True).returncode == 0
    applied = applicable(reverse=True)
    old_patch = next((str(ROOT/'patches'/name) for name in
                      ['v2-character-menu.patch', 'v1-character-menu.patch']
                      if not applied and applicable(reverse=True, path=str(ROOT/'patches'/name))), None)
    legacy = old_patch is not None
    if not applied and not legacy and not applicable():
        raise RuntimeError('The SDK menu/build files conflict with the patch; no files were changed.')
    integration = ['esp32/components/muse/CMakeLists.txt', 'esp32/components/muse/muse_menu.c',
                   'esp32/components/muse/muse_settings_ui.c']
    if legacy:
        # Validate the complete migration in isolation before touching the SDK.
        with tempfile.TemporaryDirectory(prefix='celery-man-upgrade-') as tmp:
            for name in integration:
                target = Path(tmp)/name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(sdk/name, target)
            subprocess.run(['git', 'apply', '--reverse', old_patch], cwd=tmp, check=True)
            subprocess.run(['git', 'apply', '--check', patch], cwd=tmp, check=True)
    old_hashes = json.loads((ROOT/'patches/v1-runtime-sha256.json').read_text())
    avatar = component / 'avatar'
    if avatar.is_symlink() or any((avatar / f).is_symlink() for f in RUNTIME):
        raise RuntimeError('Refusing to install through an avatar symlink.')
    for name in RUNTIME:
        source, target = ROOT / 'avatar' / name, avatar / name
        if target.parent.is_symlink():
            raise RuntimeError(f'Refusing to install through symlink: {target.parent}')
        known_old = legacy and target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == old_hashes.get(name)
        if target.exists() and not known_old and (not target.is_file() or target.read_bytes() != source.read_bytes()):
            raise RuntimeError(f'Existing custom avatar file differs: {target}. Back it up separately before installing.')
    if check:
        print('Compatible. Menu patch ' + ('already applied.' if applied else 'ready to upgrade.' if legacy else 'ready to apply.'))
        return
    touched = [sdk/name for name in integration] + [avatar/name for name in RUNTIME]
    previous = {p: p.read_bytes() if p.exists() else None for p in touched}
    try:
        if legacy:
            subprocess.run(git + ['apply', '--reverse', old_patch], check=True)
        if not applied:
            subprocess.run(git + ['apply', patch], check=True)
        for name in RUNTIME:
            target = avatar / name
            if not target.exists() or target.read_bytes() != (ROOT/'avatar'/name).read_bytes():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / 'avatar' / name, target)
    except Exception:
        for target, data in previous.items():
            if data is None: target.unlink(missing_ok=True)
            else: target.write_bytes(data)
        raise
    print(f'Installed Tayne, Celery Man, Oyster and the default-pet integration into {avatar}')
    print('Next: choose your board and follow INSTALL.md to configure and build.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sdk', type=Path, help='Path to the muse-gadget-sdk repository')
    parser.add_argument('--check', action='store_true', help='Check compatibility without writing')
    args = parser.parse_args()
    try:
        install(args.sdk, args.check)
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
