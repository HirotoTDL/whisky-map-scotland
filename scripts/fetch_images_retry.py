#!/usr/bin/env python
"""
Wikimedia Commons APIで直接 "<名前> Distillery" 画像を検索。
"""
import json
import urllib.request
import urllib.parse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DETAILS_FILE = ROOT / 'data' / 'details.json'

RETRY_LIST = [
    ('glenfiddich', 'Glenfiddich'),
    ('springbank', 'Springbank distillery'),
    ('glenrothes', 'Glenrothes distillery'),
    ('lochranza', 'Lochranza distillery'),
    ('wolfburn', 'Wolfburn distillery'),
    ('holyrood', 'Holyrood distillery Edinburgh'),
    ('lochlea', 'Lochlea distillery'),
    ('dornoch', 'Dornoch Castle distillery'),
    ('kininvie', 'Kininvie distillery Dufftown'),
    ('ailsa_bay', 'Ailsa Bay distillery Girvan'),
    ('glasgow', 'Glasgow 1770 distillery Hillington'),
    ('isle_of_harris', 'Isle of Harris distillery Tarbert'),
    ('bonnington', 'Bonnington distillery Leith'),
    ('glenwyvis', 'GlenWyvis distillery Dingwall'),
    ('strathearn', 'Strathearn distillery Methven'),
    ('ardross', 'Ardross distillery'),
    ('dunphail', 'Dunphail distillery Bimber'),
]


def search_commons_image(query):
    """Wikimedia Commons でファイル画像を検索"""
    url = ('https://commons.wikimedia.org/w/api.php?'
           + urllib.parse.urlencode({
               'action': 'query',
               'list': 'search',
               'srsearch': query + ' filetype:bitmap',
               'srnamespace': '6',  # File namespace
               'format': 'json',
               'srlimit': '5',
           }))
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'WhiskyMap/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        results = data.get('query', {}).get('search', [])
        for r in results:
            title = r['title']  # e.g. "File:Glenfiddich distillery.jpg"
            if title.startswith('File:'):
                filename = title[5:]
                # Skip logos / maps / unrelated
                low = filename.lower()
                if any(k in low for k in ['logo', 'label', 'map', 'coat', 'sign']):
                    continue
                return get_file_url(filename)
    except Exception as e:
        print(f'  search error {query}: {e}', file=sys.stderr)
    return None


def get_file_url(filename):
    """File name から直接画像URLを取得"""
    url = ('https://en.wikipedia.org/w/api.php?'
           + urllib.parse.urlencode({
               'action': 'query',
               'titles': 'File:' + filename,
               'prop': 'imageinfo',
               'iiprop': 'url',
               'iiurlwidth': '800',
               'format': 'json',
           }))
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'WhiskyMap/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        pages = data.get('query', {}).get('pages', {})
        for pid, page in pages.items():
            info = page.get('imageinfo', [])
            if info:
                return info[0].get('thumburl') or info[0].get('url')
    except Exception as e:
        print(f'  file url error {filename}: {e}', file=sys.stderr)
    return None


def main():
    with open(DETAILS_FILE, encoding='utf-8') as f:
        details = json.load(f)
    updated = 0
    still_missing = []
    for did, query in RETRY_LIST:
        if did not in details:
            continue
        img = search_commons_image(query)
        if img:
            details[did]['image'] = img
            updated += 1
            print(f'  OK  {did}: {img}')
        else:
            still_missing.append((did, query))
            print(f'  NG  {did}: {query}')
        time.sleep(0.3)
    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print(f'\n{updated} recovered, {len(still_missing)} still missing')
    for did, q in still_missing:
        print(f'  - {did}: {q}')


if __name__ == '__main__':
    main()
