"""Inspect/install the checked soundtrack catalog; never publish or generate audio."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from yt_pipeline.core import Workspace
from yt_pipeline.curated_music import install_music_catalog, music_catalog, select_genre_music, GENRES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(ROOT / 'data/pipeline'))
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    install = sub.add_parser('install')
    install.add_argument('--key', action='append', help='Repeat to install selected keys; omitted means all permitted recordings.')
    choose = sub.add_parser('select')
    choose.add_argument('genre', choices=GENRES)
    choose.add_argument('--selection-key', default='')
    args = parser.parse_args()
    if args.command == 'list':
        result = music_catalog()
    elif args.command == 'install':
        result = install_music_catalog(Workspace(args.root), args.key)
    else:
        result = select_genre_music(Workspace(args.root), args.genre, args.selection_key)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
