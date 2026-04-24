#!/usr/bin/env python
"""
ボトル画像URLから建物/樽などの無関係画像を除去する。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DETAILS_FILE = ROOT / 'data' / 'details.json'


def is_valid_bottle_image(url):
    """ファイル名から、実際のボトル画像かを判定"""
    if not url:
        return False
    low = url.lower()
    # Must contain 'bottle' or 'yo' (year old) or year number like '12y' or distillery name alone
    # Reject clear non-bottle images
    reject_keywords = [
        'distillery_-_', 'distillery-',  # geograph style
        'casks_and', 'casks-and',
        'distiller',  # often distillery building
        '9860',  # geograph IDs
        'panorama',
        'landscape',
        'stills',  # stills, not bottles
    ]
    for kw in reject_keywords:
        if kw in low:
            return False
    # Accept if contains 'bottle' or typical bottle markers
    accept_keywords = ['bottle', 'yo.jpg', 'years_old', 'year_old', 'doublewood', 'a%27bunadh', 'abunadh',
                       '12y', '15y', '18y', '10y', '25y', 'miniat', 'aged_12', 'aged_15', 'aged_18',
                       'single_malt', 'single_high', 'islay_ba']
    for kw in accept_keywords:
        if kw in low:
            return True
    return False


def main():
    with open(DETAILS_FILE, encoding='utf-8') as f:
        details = json.load(f)
    cleaned = 0
    kept = 0
    for did, data in details.items():
        if did.startswith('_'):
            continue
        for section in ('core', 'limited'):
            bottles = data.get('bottles', {}).get(section, [])
            for bottle in bottles:
                if not bottle.get('image'):
                    continue
                if not is_valid_bottle_image(bottle['image']):
                    print(f'  REMOVE {did} [{section}] "{bottle["name"]}": {bottle["image"][:80]}')
                    bottle['image'] = ''
                    cleaned += 1
                else:
                    kept += 1
    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print(f'\nCleaned: {cleaned}, Kept: {kept}')


if __name__ == '__main__':
    main()
