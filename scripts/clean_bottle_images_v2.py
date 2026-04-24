#!/usr/bin/env python
"""
Bottle画像から建物/風景を除去。より精密なフィルタ。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DETAILS_FILE = ROOT / 'data' / 'details.json'

# 明確にボトル画像とわかるキーワード(これがあれば残す)
BOTTLE_KEYWORDS = [
    'bottle', 'bottles',
    'a_bottle_of',
    'abunadh', "a%27bunadh", 'a%27bunadh',
    'single_malt_scotch', 'single_malt_whisky',
    'aged_12', 'aged_15', 'aged_18', 'aged_25', 'aged_30', 'aged_40',
    '12_years', '15_years', '18_years', '25_years',
    '12yo', '15yo', '18yo', '25yo', '10yo',
    'majors_reserve', 'doublewood', 'solstice',
    'miniature', 'miniat',
    '_barley_', 'islay_barley', 'bere_barley',
    'black_art', 'organic_scottish',
    'corryvreckan', 'wee_beastie', 'an_oa',
    'oak.jpg', 'american_oak',
    'quarter_cask',
    'sanaig', 'loch_gorm', 'machir_bay_kilchoman',
    'glenmorangie_10', 'glenmorangie_18', 'glenmorangie_quinta', 'signet',
    'glenfiddich_12', 'glenfiddich_15', 'glenfiddich_18', 'glenfiddich_grande',
    'talisker_10', 'talisker_18', 'talisker_dark', 'talisker_storm',
    'ardbeg_ten', 'ardbeg_wee_beastie', 'ardbeg_an_oa', 'ardbeg_corryvreckan',
    'ardbeg_uigeadail',
    'laphroaig_10', 'laphroaig_quarter', 'laphroaig_select',
    'lagavulin_16', 'lagavulin_8', 'lagavulin_12', 'lagavulin_beschn',
    'lagavulin_islay_single',
    'macallan_', 'balvenie_',
    'bowmore_12', 'bowmore_15', 'bowmore_18', 'bowmore_bottle',
    'dalmore_12', 'dalmore_18', 'dalmore_king',
    'glenlivet_12', 'glenlivet_15', 'glenlivet_single',
    'glenlivet_founder',
    'oban-14', 'oban_14',
    'springbank_aged',
    'dalwhinnie_single',
    'glenkinchie_single',
    'auchentoshan_american',
    'clynelish_single',
]

# 明確に建物/風景の画像(これがあれば除外)
BAD_KEYWORDS = [
    'geograph',
    'panoramio',
    'distillery_-_', 'distillery-_', '_distillery.jpg', 'distillery.jpg',
    '_arch_', 'arch_',
    'visitor', 'visitorcenter',
    'fishing_boats',
    'chocolate_',
    'william_street',
    'bute_',
    'from_the_air',
    'entrance',
    '_bay_-_panoramio',
    'street',
    'street_',
    'from_above',
    'aerial',
    'cooperage',
    'panorama',
    'the_bunnahabhain_distillery_',
    'caol_ila_distillery',
    'benromach_distillery',
    'glendronach_visitor',
    'glendronach_distillery',
    'springbank_%',
    'dalwhinnie_distillery',
    '_tube',
]


def is_bottle_url(url):
    if not url:
        return False
    low = url.lower()
    filename = low.split('/')[-1]
    # Check bad first
    for bad in BAD_KEYWORDS:
        if bad in filename:
            # Allow if bottle keyword also present
            for good in BOTTLE_KEYWORDS:
                if good in filename:
                    return True
            return False
    # Then good
    for good in BOTTLE_KEYWORDS:
        if good in filename:
            return True
    # Fall through - if nothing matches, conservative reject
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
                if is_bottle_url(bottle['image']):
                    kept += 1
                else:
                    fn = bottle['image'].split('/')[-1][:60]
                    print(f'  REMOVE {did} "{bottle["name"][:30]}": {fn}')
                    bottle['image'] = ''
                    cleaned += 1
    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print(f'\nCleaned: {cleaned}, Kept: {kept}')


if __name__ == '__main__':
    main()
