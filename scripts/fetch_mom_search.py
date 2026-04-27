#!/usr/bin/env python
"""MoMのsearch endpointから残り蒸留所のボトル画像を取得"""
import urllib.request
import urllib.parse
import re
import json
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36')

# Distillery name → MoM search query
SEARCH = {
    'lochlea':        'Lochlea',
    'lagg':           'Lagg',
    'glasgow':        'Glasgow 1770',
    'clydeside':      'Stobcross',
    'isle_of_raasay': 'Raasay',
    'torabhaig':      'Torabhaig',
    'ardnamurchan':   'Ardnamurchan AD',
    'ncnean':         "Nc'nean",
    'saxa_vord':      'Saxa Vord',
    'port_of_leith':  'Port of Leith',
    'borders':        'Borders Distillery',
    'falkirk':        'Falkirk',
    'aberargie':      'Aberargie',
    'dunphail':       'Dunphail',
    'cabrach':        'Cabrach',
    'dalmunach':      'Dalmunach',
    'roseisle':       'Roseisle',
    'bonnington':     'Bonnington',
    'ardross':        'Ardross',
    'ardgowan':       'Ardgowan',
    'uilebheist':     'Uile-bheist',
    'inchdairnie':    'InchDairnie',
    'annandale':      'Annandale',
    'arbikie':        'Arbikie',
    'glenwyvis':      'GlenWyvis',
    'glengyle':       'Kilkerran',
}


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode('utf-8', errors='ignore')


def parse(html, query):
    pattern = r'<img[^>]*alt="([^"]+)"[^>]*src="(https://cdn11\.bigcommerce\.com/[^"]+)"'
    matches = re.findall(pattern, html)
    seen = set()
    out = []
    qparts = query.lower().split()
    for alt, src in matches:
        if alt in seen:
            continue
        seen.add(alt)
        alt_l = alt.lower()
        # Must contain at least one core word from query
        if any(p in alt_l for p in qparts if len(p) >= 4):
            out.append({'name': alt, 'image': src})
    return out


def main():
    output = {}
    for did, query in SEARCH.items():
        url = 'https://www.masterofmalt.com/search/?searchTerm=' + urllib.parse.quote(query)
        try:
            html = fetch(url)
            products = parse(html, query)
            output[did] = products
            print(f'[{did}] q="{query}": {len(products)} products', file=sys.stderr)
        except Exception as e:
            print(f'[{did}] ERROR: {e}', file=sys.stderr)
            output[did] = []
        time.sleep(0.5)
    with open(ROOT / 'scripts' / 'mom_search_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    total = sum(len(v) for v in output.values())
    print(f'Saved {total} products', file=sys.stderr)


if __name__ == '__main__':
    main()
