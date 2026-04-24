#!/usr/bin/env python
"""
主要ボトルの画像URLをWikimedia Commonsで検索。
"""
import json
import urllib.request
import urllib.parse
import sys
import time
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DETAILS_FILE = ROOT / 'data' / 'details.json'


def search_commons(query):
    url = ('https://commons.wikimedia.org/w/api.php?'
           + urllib.parse.urlencode({
               'action': 'query',
               'list': 'search',
               'srsearch': query + ' filetype:bitmap',
               'srnamespace': '6',
               'format': 'json',
               'srlimit': '5',
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
               'iiurlwidth': '400',
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


def find_bottle_image(distillery_name, bottle_name):
    """ボトル画像を検索。"""
    # Clean bottle name - remove parenthetical notes
    cleaned = re.sub(r'\([^)]*\)', '', bottle_name).strip()
    # Try distillery + bottle
    queries = [
        f'"{distillery_name}" {cleaned} bottle',
        f'{distillery_name} {cleaned} whisky',
    ]
    for q in queries:
        results = search_commons(q)
        for r in results:
            title = r['title']
            if not title.startswith('File:'):
                continue
            fn = title[5:]
            low = fn.lower()
            if any(k in low for k in ['logo', 'label only', 'map', 'coat', 'distillery-', 'distillery_-', 'geograph']):
                continue
            # Only accept if distillery name is in filename
            d_low = distillery_name.lower().replace(' ', '')
            if d_low not in low.replace(' ', '').replace('_', '').replace('-', ''):
                continue
            url = get_file_url(fn)
            if url:
                return url
    return None


# Top 20 most famous distilleries to try
TARGET_DISTILLERIES = [
    ('macallan', 'Macallan'),
    ('ardbeg', 'Ardbeg'),
    ('lagavulin', 'Lagavulin'),
    ('laphroaig', 'Laphroaig'),
    ('glenfiddich', 'Glenfiddich'),
    ('glenmorangie', 'Glenmorangie'),
    ('talisker', 'Talisker'),
    ('highland_park', 'Highland Park'),
    ('bowmore', 'Bowmore'),
    ('glenlivet', 'Glenlivet'),
    ('dalmore', 'Dalmore'),
    ('balvenie', 'Balvenie'),
    ('aberlour', 'Aberlour'),
    ('springbank', 'Springbank'),
    ('dalwhinnie', 'Dalwhinnie'),
    ('oban', 'Oban'),
    ('glenfarclas', 'Glenfarclas'),
    ('bunnahabhain', 'Bunnahabhain'),
    ('caol_ila', 'Caol Ila'),
    ('bruichladdich', 'Bruichladdich'),
    ('kilchoman', 'Kilchoman'),
]


def main():
    with open(DETAILS_FILE, encoding='utf-8') as f:
        details = json.load(f)
    found_count = 0
    for did, dname in TARGET_DISTILLERIES:
        if did not in details:
            continue
        data = details[did]
        for section in ('core', 'limited'):
            bottles = data.get('bottles', {}).get(section, [])
            for i, bottle in enumerate(bottles):
                if bottle.get('image'):
                    continue
                img = find_bottle_image(dname, bottle['name'])
                if img:
                    bottle['image'] = img
                    found_count += 1
                    print(f'  OK  {did} [{section}] "{bottle["name"]}": {img[:80]}')
                time.sleep(0.2)
    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print(f'\n{found_count} bottle images added')


if __name__ == '__main__':
    main()
