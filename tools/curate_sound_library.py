"""List/install/select the local SFX and ambience catalog; never publish."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from yt_pipeline.core import Workspace
from yt_pipeline.sound_library import install_sound_library, sound_catalog, select_sound


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(ROOT / 'data/pipeline'))
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    install = sub.add_parser('install')
    install.add_argument('--originals-only', action='store_true', help='Create original UI signals without downloading ambience.')
    install.add_argument('--key', action='append')
    select = sub.add_parser('select')
    select.add_argument('category')
    select.add_argument('--selection-key', default='')
    select.add_argument('--genre')
    args = parser.parse_args()
    if args.command == 'list':
        result = sound_catalog()
    elif args.command == 'install':
        result = install_sound_library(Workspace(args.root), not args.originals_only, args.key)
    else:
        result = select_sound(Workspace(args.root), args.category, args.selection_key, args.genre)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
