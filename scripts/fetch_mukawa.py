#!/usr/bin/env python
"""武川蒸留酒販売(mukawa-spirit.com)から残り蒸留所のボトル画像を取得"""
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

# Distilleries to search with their Japanese katakana name
SEARCHES = {
    'lochlea':        'ロッホリー',
    'lagg':           'ラグ',
    'glasgow':        '1770',  # Glasgow 1770 brand
    'clydeside':      'クライドサイド',
    'isle_of_raasay': 'ラッセイ',
    'torabhaig':      'トラベイグ',
    'ardnamurchan':   'アードナマッカン',
    'ncnean':         'ノックニーアン',
    'saxa_vord':      'サクサヴォード',
    'port_of_leith':  'リース',
    'borders':        'ボーダーズ',
    'falkirk':        'ファルカーク',
    'aberargie':      'アベラーギ',
    'dunphail':       'ダンフェイル',
    'cabrach':        'カブラック',
    'dalmunach':      'ダルムナック',
    'roseisle':       'ローズアイル',
    'bonnington':     'ボニントン',
    'ardross':        'アードロス',
    'ardgowan':       'アードゴーワン',
    'uilebheist':     'ユーレビースト',
    'inchdairnie':    'インチデアニー',
    'annandale':      'アナンデール',
    'arbikie':        'アービッキー',
    'glenwyvis':      'グレンウィヴィス',
    'glengyle':       'キルケラン',  # Kilkerran brand
    # Also retry some that returned weak matches
    'wolfburn':       'ウルフバーン',
    'kingsbarns':     'キングスバーンズ',
    'holyrood':       'ホーリールード',
    'lindores_abbey': 'リンドアズアビー',
    'ailsa_bay':      'アイルサベイ',
    'aerstone':       'エアストーン',  # Ailsa Bay's Aerstone brand
    'speyburn':       'スペイバーン',
    'kininvie':       'キニンヴィ',
    'tullibardine':   'タリバーディン',
}


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en;q=0.9',
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        # Site uses EUC-JP
        return r.read().decode('euc_jp', errors='ignore')


def parse_products(html):
    """Extract product name + image URL from mukawa-spirit search results"""
    # The site uses Shop-Pro template. Product images are in file002.shop-pro.jp
    # Look for product blocks with img and product name links
    # Pattern: <a href="?pid=N"...><img src="...thumbnail..."  alt="<name>" ...>
    # First: find all anchor + img + name patterns
    # Try to match product card structure
    pattern = r'<a[^>]+href="[^"]*pid=(\d+)"[^>]*>.*?<img[^>]+src="(https?://file002\.shop-pro\.jp/[^"]+)"[^>]+alt="([^"]+)"'
    matches = re.findall(pattern, html, re.DOTALL)
    seen = set()
    out = []
    for pid, src, alt in matches:
        if pid in seen or not alt.strip():
            continue
        seen.add(pid)
        # Filter out non-product images (icons, banners)
        if any(x in src.lower() for x in ['icon', 'logo', 'banner', 'common/']):
            continue
        out.append({'pid': pid, 'name': alt.strip(), 'image': src})
    return out


def parse_simpler(html):
    """Fallback parser: extract just product image URLs and infer name from nearby text"""
    # Extract /shopdetail/ links with images
    pattern = r'<img[^>]+src="(https?://file002\.shop-pro\.jp/PA01356/[^"]+)"[^>]*alt="([^"]*)"'
    matches = re.findall(pattern, html)
    out = []
    seen = set()
    for src, alt in matches:
        if src in seen:
            continue
        seen.add(src)
        if any(x in src.lower() for x in ['icon', 'logo', 'banner', 'common/', 'assets/image/common']):
            continue
        if not alt or alt.startswith('武川') or len(alt) < 3:
            continue
        out.append({'name': alt.strip(), 'image': src})
    return out


def search_one(query):
    # EUC-JP encode the keyword
    encoded = urllib.parse.quote(query.encode('euc-jp'))
    url = f'https://mukawa-spirit.com/?mode=srh&cid=&keyword={encoded}'
    html = fetch(url)
    products = parse_products(html)
    if not products:
        products = parse_simpler(html)
    return products


def main():
    output = {}
    for did, query in SEARCHES.items():
        try:
            products = search_one(query)
            output[did] = products
            print(f'[{did}] q="{query}": {len(products)} products', file=sys.stderr)
        except Exception as e:
            print(f'[{did}] ERROR: {e}', file=sys.stderr)
            output[did] = []
        time.sleep(0.6)
    out_path = ROOT / 'scripts' / 'mukawa_results.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    total = sum(len(v) for v in output.values())
    print(f'Saved {total} products', file=sys.stderr)


if __name__ == '__main__':
    main()
