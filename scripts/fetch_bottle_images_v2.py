#!/usr/bin/env python
"""
ボトル画像をWikimedia Commonsで検索。より精密なマッチング。
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


def is_building_or_landscape(filename):
    """建物/風景画像をフィルタ"""
    low = filename.lower()
    bad_terms = [
        'geograph',
        'distillery_-_', 'distillery-_',
        'casks_and', 'casks-and',
        'panorama',
        'from_the_air',
        'aerial',
        'from_above',
        'the_view',
        'landscape',
        'stills_', 'stills-',
        'warehouse',
        'entrance',
        'sign',
        'building',
        'road_',
        'view_',
        'gruen_voll', 'blau_voll',  # German angle shots of bottle interior?
    ]
    for t in bad_terms:
        if t in low:
            # But allow if it's clearly a bottle image variant
            if 'bottle' in low or '_yo.jpg' in low or 'bottles' in low:
                continue
            return True
    return False


def find_bottle_image(distillery_name, bottle_name):
    cleaned = re.sub(r'\([^)]*\)', '', bottle_name).strip()
    queries = [
        f'{distillery_name} {cleaned}',
        f'"{distillery_name}" {cleaned}',
    ]
    d_key = distillery_name.lower().replace(' ', '').replace("'", '')
    for q in queries:
        results = search_commons(q)
        for r in results:
            title = r['title']
            if not title.startswith('File:'):
                continue
            fn = title[5:]
            low = fn.lower()
            # Skip SVG logos
            if 'logo' in low or '.svg' in low:
                continue
            # Must contain distillery name root
            name_root = d_key.replace('-', '').replace('_', '')
            fn_norm = low.replace(' ', '').replace('_', '').replace('-', '').replace("'", '').replace('%27','')
            if name_root not in fn_norm:
                continue
            # Skip obvious buildings
            if is_building_or_landscape(fn):
                continue
            url = get_file_url(fn)
            if url:
                return url
    return None


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
    ('glen_grant', 'Glen Grant'),
    ('benromach', 'Benromach'),
    ('benriach', 'BenRiach'),
    ('glendronach', 'Glendronach'),
    ('glenkinchie', 'Glenkinchie'),
    ('auchentoshan', 'Auchentoshan'),
    ('clynelish', 'Clynelish'),
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
            for bottle in bottles:
                if bottle.get('image'):
                    continue
                img = find_bottle_image(dname, bottle['name'])
                if img:
                    bottle['image'] = img
                    found_count += 1
                    print(f'  OK  {did} [{section}] "{bottle["name"][:35]}": {img.split("/")[-1][:50]}')
                time.sleep(1.2)
    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print(f'\n{found_count} bottle images added')


if __name__ == '__main__':
    main()
