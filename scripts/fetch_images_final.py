#!/usr/bin/env python
"""
残り画像: Google Image搜索の代わりに、Wikimedia Commonsの複数ソースから試す。
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
    ('lochlea', ['Lochlea farm distillery', 'Lochlea Tarbolton']),
    ('dornoch', ['Dornoch fire station', 'Dornoch Castle']),
    ('ailsa_bay', ['Girvan distillery', 'William Grant Ailsa']),
    ('glasgow', ['Glasgow Distillery Hillington', '1770 Glasgow']),
    ('glenwyvis', ['Dingwall distillery', 'GlenWyvis']),
    ('strathearn', ['Strathearn Perthshire', 'Methven distillery']),
    ('dunphail', ['Dunphail Moray', 'Bimber Dunphail']),
    ('bonnington', ['Halewood Leith', 'Bonnington Edinburgh whisky']),
    ('kininvie', ['Balvenie Kininvie', 'William Grant Kininvie']),
]


def search_commons(query):
    """Commons で画像検索。マッピング不適合はスキップ"""
    url = ('https://commons.wikimedia.org/w/api.php?'
           + urllib.parse.urlencode({
               'action': 'query',
               'list': 'search',
               'srsearch': query + ' filetype:bitmap',
               'srnamespace': '6',
               'format': 'json',
               'srlimit': '10',
           }))
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'WhiskyMap/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data.get('query', {}).get('search', [])
    except Exception as e:
        print(f'  search error {query}: {e}', file=sys.stderr)
    return []


def get_file_url(filename):
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
    except Exception:
        pass
    return None


def main():
    with open(DETAILS_FILE, encoding='utf-8') as f:
        details = json.load(f)
    updated = 0
    for did, queries in RETRY_LIST:
        if did not in details:
            continue
        found = None
        for q in queries:
            results = search_commons(q)
            for r in results:
                title = r['title']
                if not title.startswith('File:'):
                    continue
                fn = title[5:]
                low = fn.lower()
                if any(k in low for k in ['logo', 'label', 'map', 'coat', 'sign', 'road sign']):
                    continue
                # Prefer filenames mentioning the distillery name keyword
                q_kw = q.split()[0].lower()
                if q_kw not in low:
                    continue
                url = get_file_url(fn)
                if url:
                    found = url
                    break
            if found:
                break
            time.sleep(0.2)
        if found:
            details[did]['image'] = found
            updated += 1
            print(f'  OK  {did}: {found}')
        else:
            print(f'  NG  {did}')
        time.sleep(0.3)
    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print(f'\n{updated} updated')


if __name__ == '__main__':
    main()
