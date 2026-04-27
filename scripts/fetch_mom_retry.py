#!/usr/bin/env python
"""失敗した404蒸留所を別の slug で再試行"""
import urllib.request
import re
import json
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36')

# Multiple slug attempts per distillery
RETRY = {
    'lochlea':        ['lochlea-distillery'],
    'lagg':           ['lagg-distillery'],
    'glasgow':        ['glasgow-1770-whisky-distillery', 'glasgow-distillery-co', 'the-glasgow-distillery'],
    'holyrood':       ['holyrood-distillery', 'the-holyrood-distillery'],
    'lindores_abbey': ['lindores-abbey-whisky-distillery', 'lindores-abbey'],
    'clydeside':      ['clydeside-whisky-distillery', 'the-clydeside-distillery'],
    'isle_of_raasay': ['isle-of-raasay-whisky-distillery', 'raasay-whisky-distillery', 'raasay-distillery'],
    'torabhaig':      ['torabhaig-whisky-distillery'],
    'ardnamurchan':   ['ardnamurchan-whisky-distillery'],
    'ncnean':         ['nc-nean-whisky-distillery', 'nc-nean-distillery', 'ncnean-distillery'],
    'saxa_vord':      ['saxa-vord-whisky-distillery'],
    'port_of_leith':  ['port-of-leith-whisky-distillery', 'the-port-of-leith-distillery'],
    'borders':        ['borders-distillery', 'the-borders-distillery'],
    'falkirk':        ['falkirk-whisky-distillery', 'the-falkirk-distillery'],
    'aberargie':      ['aberargie-whisky-distillery'],
    'dunphail':       ['dunphail-distillery'],
    'cabrach':        ['cabrach-distillery', 'the-cabrach-distillery'],
    'dalmunach':      ['dalmunach-whisky-distillery'],
    'roseisle':       ['roseisle-whisky-distillery'],
    'bonnington':     ['bonnington-distillery'],
    'ardross':        ['ardross-whisky-distillery'],
    'ardgowan':       ['ardgowan-whisky-distillery'],
    'uilebheist':     ['uile-bheist-whisky-distillery', 'uilebheist-distillery', 'uilebheist-whisky-distillery'],
    'daftmill':       ['daftmill-whisky-distillery'],
    'inchdairnie':    ['inchdairnie-whisky-distillery'],
    'annandale':      ['annandale-distillery'],
    'arbikie':        ['arbikie-highland-estate-distillery', 'arbikie-distillery-whisky', 'arbikie-whisky-distillery'],
    'glenwyvis':      ['glen-wyvis-whisky-distillery'],
    'glengyle':       ['kilkerran-glengyle-whisky-distillery', 'kilkerran-whisky-distillery'],
    # Try search instead for known-failed
}


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode('utf-8', errors='ignore')


def parse(html, dn):
    pattern = r'<img[^>]*alt="([^"]+)"[^>]*src="(https://cdn11\.bigcommerce\.com/[^"]+)"'
    matches = re.findall(pattern, html)
    seen = set()
    out = []
    dn_l = dn.lower()
    for alt, src in matches:
        if alt in seen:
            continue
        seen.add(alt)
        if any(p in alt.lower() for p in dn_l.split()):
            out.append({'name': alt, 'image': src})
    return out


def main():
    output = {}
    for did, slugs in RETRY.items():
        dn = did.replace('_', ' ')
        for slug in slugs:
            url = f'https://www.masterofmalt.com/distilleries/{slug}/'
            try:
                html = fetch(url)
                products = parse(html, dn)
                if products:
                    print(f'[{did}] slug={slug}: {len(products)} products', file=sys.stderr)
                    output[did] = products
                    break
            except Exception as e:
                continue
            time.sleep(0.4)
        else:
            print(f'[{did}] no products found in any slug', file=sys.stderr)

    out_path = ROOT / 'scripts' / 'mom_retry_results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f'Saved to {out_path}', file=sys.stderr)


if __name__ == '__main__':
    main()
