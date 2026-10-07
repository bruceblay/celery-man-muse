#!/usr/bin/env python3
"""Install the character pack into an existing Muse Gadget SDK checkout."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REVISION = '1b56662588c0ea00bdee24b9bcd1835e12848e9a'
RUNTIME = ['muse_pixel.c', 'characters.h'] + [
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
    def applicable(reverse=False):
        args = git + ['apply', '--check'] + (['--reverse'] if reverse else []) + [patch]
        return subprocess.run(args, capture_output=True).returncode == 0
    applied = applicable(reverse=True)
    if not applied and not applicable():
        raise RuntimeError('The SDK menu/build files conflict with the patch; no files were changed.')
    avatar = component / 'avatar'
    if avatar.is_symlink() or any((avatar / f).is_symlink() for f in RUNTIME):
        raise RuntimeError('Refusing to install through an avatar symlink.')
    for name in RUNTIME:
        source, target = ROOT / 'avatar' / name, avatar / name
        if target.parent.is_symlink():
            raise RuntimeError(f'Refusing to install through symlink: {target.parent}')
        if target.exists() and (not target.is_file() or target.read_bytes() != source.read_bytes()):
            raise RuntimeError(f'Existing custom avatar file differs: {target}. Back it up separately before installing.')
    if check:
        print('Compatible. Menu patch ' + ('already applied.' if applied else 'ready to apply.'))
        return
    created = []
    patched = False
    try:
        if not applied:
            subprocess.run(git + ['apply', patch], check=True)
            patched = True
        for name in RUNTIME:
            target = avatar / name
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                created.append(target)
                shutil.copyfile(ROOT / 'avatar' / name, target)
    except Exception:
        for target in reversed(created):
            target.unlink(missing_ok=True)
        if patched:
            subprocess.run(git + ['apply', '--reverse', patch], check=True)
        raise
    print(f'Installed Tayne, Celery Man and Oyster into {avatar}')
    print('Next: configure and build the StickS3 firmware using the README.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sdk', type=Path, help='Path to the muse-gadget-sdk repository')
    parser.add_argument('--check', action='store_true', help='Check compatibility without writing')
    args = parser.parse_args()
    try:
        install(args.sdk, args.check)
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
