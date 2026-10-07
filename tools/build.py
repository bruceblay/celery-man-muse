#!/usr/bin/env python3
"""Configure, build or flash a character-pack firmware for a Muse UI board."""
import argparse
from pathlib import Path
import shlex
import subprocess
import sys

from boards import BOARDS
from install import install

ROOT = Path(__file__).resolve().parents[1]


def command(board, action, port=None):
    profile = BOARDS[board]
    if action == 'flash':
        if not port:
            raise ValueError('Flashing requires --port for the identified board.')
        return ['bash', 'tools/muse/board.sh', 'flash', board, port]
    build = f'build-muse-{profile.profile}'
    return ['idf.py', '-B', build, f'-DIDF_TARGET={profile.target}',
            f'-DSDKCONFIG={build}/sdkconfig',
            '-DSDKCONFIG_DEFAULTS=sdkconfig.defaults;devices/sdkconfig.muse;'
            f'devices/sdkconfig.muse-{profile.profile}',
            'menuconfig' if action == 'configure' else 'build']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('board', choices=BOARDS, nargs='?')
    parser.add_argument('action', choices=['configure', 'build', 'flash'], nargs='?', default='build')
    parser.add_argument('--sdk', type=Path, default=ROOT.parent/'muse-gadget-sdk')
    parser.add_argument('--port')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--dry-run', action='store_true', help='Print the command without writing or building')
    args = parser.parse_args()
    if args.list:
        for key, board in BOARDS.items():
            print(f'{key:8} {board.width}x{board.height:3}  {"touch" if board.touch else "buttons":7} {board.name}')
        return
    if not args.board:
        parser.error('Choose a board, or use --list.')
    if args.port and args.action != 'flash':
        parser.error('--port is used only for flash.')
    try:
        cmd = command(args.board, args.action, args.port)
        sdk = args.sdk.resolve()
        if args.dry_run:
            print(f'Working directory: {sdk / "esp32"}')
            print(shlex.join(cmd))
            return
        if args.action != 'flash':
            version = subprocess.check_output(['idf.py', '--version'], text=True).strip()
            if not version.startswith('ESP-IDF v6.0.1'):
                raise RuntimeError(f'Activate ESP-IDF v6.0.1; found {version}.')
            install(sdk)
        else:
            binary = sdk/'esp32'/f'build-muse-{BOARDS[args.board].profile}'/'muse-gadget.bin'
            if not binary.is_file():
                raise RuntimeError('Build this board before flashing it.')
        subprocess.run(cmd, cwd=sdk/'esp32', check=True)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        sys.exit(str(error))


if __name__ == '__main__':
    main()
