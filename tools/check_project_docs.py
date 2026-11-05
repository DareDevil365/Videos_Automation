"""Check managed local Markdown links and the documentation move map offline."""
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def main():
    files = sorted({*ROOT.glob('*.md'), *ROOT.glob('docs/**/*.md'),
                    *ROOT.glob('agents/**/*.md'), *ROOT.glob('research/**/*.md'),
                    *ROOT.glob('examples/**/*.md'), *ROOT.glob('tools/*.md'),
                    *ROOT.glob('src/yt_pipeline/skills/**/*.md'),
                    *ROOT.glob('tests/*.md'), *ROOT.glob('Resources/**/README.md')})
    problems = []
    links = 0
    for path in files:
        contents = path.read_text(encoding='utf-8-sig')
        for match in re.finditer(r'\]\(([^)\n]+)\)', contents):
            target = match[1].strip()
            if target.startswith('<'):
                target = target[1:target.find('>')]
            else:
                target = re.split(r'\s+[\"\']', target, maxsplit=1)[0]
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            links += 1
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.exists():
                problems.append({'file': path.relative_to(ROOT).as_posix(),
                                 'line': contents.count('\n', 0, match.start()) + 1,
                                 'target': target})
    move_path = ROOT / 'docs/FILE_MOVES.json'
    moves = json.loads(move_path.read_text(encoding='utf-8'))['moves']
    for original, destination in moves.items():
        if not (ROOT / destination).is_file():
            problems.append({'move': original, 'missing_destination': destination})
    result = {'documents': len(files), 'local_links': links, 'moves': len(moves),
              'problems': problems}
    print(json.dumps(result, indent=2))
    return bool(problems)


if __name__ == '__main__':
    sys.exit(main())
