"""Find cached comic-story evidence before starting another web search."""
from argparse import ArgumentParser
import hashlib
import json
from pathlib import Path
import re


ROOT=Path(__file__).resolve().parents[1]


def review_match(raw,review):
    """Git's LF checkout may differ from the reviewed Windows CRLF bytes only."""
    if review.get('supported') is not True:return None
    expected=review.get('brief_sha256')
    if expected==hashlib.sha256(raw).hexdigest():return 'exact'
    lf=raw.replace(b'\r\n',b'\n')
    if expected in {hashlib.sha256(lf).hexdigest(),hashlib.sha256(lf.replace(b'\n',b'\r\n')).hexdigest()}:
        return 'line_endings_only'
    return None


def lookup(query='',ready_only=False):
    library=json.loads((ROOT/'research/content-lore/source-library.json').read_text(encoding='utf-8'))
    normalize=lambda value:re.sub(r'[^a-z0-9]+','',value.casefold())
    matches=[]
    for entry in library['stories']:
        if query and normalize(query) not in normalize(' '.join([entry['id'],entry['title'],entry['issues'],*entry['tags']])):continue
        row=dict(entry)
        if row.get('project_brief'):
            path=ROOT/row['project_brief']
            if not path.is_file():
                row['packet_status']='missing'
            else:
                raw=path.read_bytes();brief=json.loads(raw)
                review_path=ROOT/row['source_review']
                review=json.loads(review_path.read_text(encoding='utf-8')) if review_path.is_file() else {}
                matched=review_match(raw,review)
                row.update(packet_status='reviewed_claim_scope' if matched else 'review_needed',packet_hash_match=matched,
                           claims=brief['claims'],sources=brief['sources'])
        else:row['packet_status']='discovery_only'
        if ready_only and row['packet_status']!='reviewed_claim_scope':continue
        matches.append(row)
    return {'matches':matches,'scope':'Cached source-linked facts, not preapproved narration. Uncached motives, scenes or endings need reading and a new claim review.'}


def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('query',nargs='?',default='')
    parser.add_argument('--ready-only',action='store_true')
    args=parser.parse_args()
    print(json.dumps(lookup(args.query,args.ready_only),ensure_ascii=True,indent=2))


if __name__=='__main__':main()
