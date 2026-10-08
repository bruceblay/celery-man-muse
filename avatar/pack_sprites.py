#!/usr/bin/env python3
"""Pack a character's approved video sheets as RGB565."""
import argparse
from pathlib import Path
import runpy

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('character', choices=['tayne', 'celery-man', 'oyster'])
args = parser.parse_args()
runpy.run_path(str(Path(__file__).resolve().parent / args.character / 'pack_sprites.py'), run_name='__main__')
