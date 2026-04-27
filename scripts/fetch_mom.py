#!/usr/bin/env python
"""Master of Malt distillery page から product image URL を取得"""
import urllib.request
import re
import json
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36')

DISTILLERIES = {
    'wolfburn':       'wolfburn-whisky-distillery',
    'lochlea':        'lochlea-whisky-distillery',
    'ailsa_bay':      'ailsa-bay-whisky-distillery',
    'lagg':           'lagg-whisky-distillery',
    'glasgow':        'glasgow-distillery',
    'holyrood':       'holyrood-whisky-distillery',
    'lindores_abbey': 'lindores-abbey-distillery',
    'clydeside':      'clydeside-distillery',
    'isle_of_raasay': 'isle-of-raasay-distillery',
    'torabhaig':      'torabhaig-distillery',
    'ardnamurchan':   'ardnamurchan-distillery',
    'kingsbarns':     'kingsbarns-whisky-distillery',
    'ncnean':         'ncnean-whisky-distillery',
    'saxa_vord':      'saxa-vord-distillery',
    'port_of_leith':  'port-of-leith-distillery',
    'dornoch':        'dornoch-distillery',
    'falkirk':        'falkirk-distillery',
    'borders':        'borders-whisky-distillery',
    'glen_ord':       'glen-ord-whisky-distillery',
    'glen_keith':     'glen-keith-whisky-distillery',
    'glentauchers':   'glentauchers-whisky-distillery',
    'dailuaine':      'dailuaine-whisky-distillery',
    'inchgower':      'inchgower-whisky-distillery',
    'teaninich':      'teaninich-whisky-distillery',
    'kininvie':       'kininvie-whisky-distillery',
    'tullibardine':   'tullibardine-whisky-distillery',
    'speyburn':       'speyburn-whisky-distillery',
    'aberargie':      'aberargie-whisky-distillery',
    'dunphail':       'dunphail-whisky-distillery',
    'cabrach':        'cabrach-whisky-distillery',
    'dalmunach':      'dalmunach-whisky-distillery',
    'braeval':        'braeval-whisky-distillery',
    'port_ellen':     'port-ellen-whisky-distillery',
    'roseisle':       'roseisle-whisky-distillery',
    'glenwyvis':      'glenwyvis-whisky-distillery',
    'aberargie':      'aberargie-distillery',
    'bonnington':     'bonnington-whisky-distillery',
    'ardross':        'ardross-distillery',
    'ardgowan':       'ardgowan-distillery',
    'uilebheist':     'uile-bheist-distillery',
    'mannochmore':    'mannochmore-whisky-distillery',
    'glenlossie':     'glenlossie-whisky-distillery',
    'auchroisk':      'auchroisk-whisky-distillery',
    'strathmill':     'strathmill-whisky-distillery',
    'glen_spey':      'glen-spey-whisky-distillery',
    'miltonduff':     'miltonduff-whisky-distillery',
    'balmenach':      'balmenach-whisky-distillery',
    'glenburgie':     'glenburgie-whisky-distillery',
    'allt_a_bhainne': 'allt-a-bhainne-whisky-distillery',
    'glengyle':       'glengyle-whisky-distillery',  # Kilkerran
    'daftmill':       'daftmill-distillery',
    'inchdairnie':    'inchdairnie-distillery',
    'annandale':      'annandale-whisky-distillery',
    'arbikie':        'arbikie-distillery',
}


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode('utf-8', errors='ignore')


def parse_products(html, distillery_name):
    """Extract bottle name + image URL pairs from MoM page"""
    # Match img tags with alt attribute and src
    # img alt="...Wolfburn..." src="https://cdn..."
    pattern = r'<img[^>]*alt="([^"]+)"[^>]*src="(https://cdn11\.bigcommerce\.com/[^"]+)"'
    matches = re.findall(pattern, html)
    products = []
    seen = set()
    dn_lower = distillery_name.lower()
    for alt, src in matches:
        if alt in seen:
            continue
        seen.add(alt)
        # Filter to only matching bottles
        alt_lower = alt.lower()
        # Distillery name should appear in alt
        if not any(part in alt_lower for part in dn_lower.split()):
            continue
        products.append({'name': alt, 'image': src})
    return products


def main():
    output = {}
    for did, slug in DISTILLERIES.items():
        url = f'https://www.masterofmalt.com/distilleries/{slug}/'
        try:
            html = fetch(url)
            # Try to detect what distillery the page is actually about
            dn = did.replace('_', ' ')
            products = parse_products(html, dn)
            output[did] = products
            print(f'[{did}] {len(products)} products', file=sys.stderr)
            time.sleep(0.5)
        except Exception as e:
            print(f'[{did}] ERROR: {e}', file=sys.stderr)
            output[did] = []
    out_path = ROOT / 'scripts' / 'mom_results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    total = sum(len(v) for v in output.values())
    print(f'Saved {total} products to {out_path}', file=sys.stderr)


if __name__ == '__main__':
    main()
