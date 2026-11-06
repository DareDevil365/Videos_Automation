"""Find cached comic-story evidence before starting another web search."""
from argparse import ArgumentParser
import hashlib
import json
from pathlib import Path
import re


ROOT=Path(__file__).resolve().parents[1]


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
                checked=review.get('supported') is True and review.get('brief_sha256')==hashlib.sha256(raw).hexdigest()
                row.update(packet_status='reviewed_claim_scope' if checked else 'review_needed',claims=brief['claims'],sources=brief['sources'])
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
