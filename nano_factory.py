import json, time, hashlib
from pathlib import Path
import requests

AKASHA = Path('./nano_output')
AKASHA.mkdir(exist_ok=True)

def fetch_topics():
    topics = []
    # commons
    r = requests.get('https://api.github.com/search/repositories?q=stars:>50000&per_page=30').json()
    topics += [x['name'] for x in r.get('items',[])]
    # corp
    for org in ['microsoft','google','meta']:
        x = requests.get(f'https://api.github.com/orgs/{org}/repos?per_page=20').json()
        if isinstance(x,list): topics += [y['name'] for y in x]
    return list(set(topics))

def mint_nano(topic):
    nid = hashlib.md5(topic.encode()).hexdigest()[:6]
    nano = f"""# NANO: {topic}
HC: {int(time.time())}
TIME: 5 minutes

## Atom 1 — Core (60s)
What is {topic} in one sentence?

## Atom 2 — Why (90s)
Why does {topic} matter to root0?

## Atom 3 — Build (120s)
Make one thing with {topic} right now.

## Atom 4 — Test (30s)
Did it work? Witness it.
---
invariant: true
"""
    (AKASHA/f'{nid}_{topic}.md').write_text(nano)
    return nid

def maxcap():
    topics = fetch_topics()
    print(f"MAX CAP: {len(topics)} topics")
    for t in topics[:200]:  # max cap = 200 per run
        mint_nano(t)
        print(f"minted {t}")
    print(f"Done. Output: {AKASHA.resolve()}")

if __name__ == '__main__':
    maxcap()