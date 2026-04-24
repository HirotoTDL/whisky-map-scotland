#!/usr/bin/env python
"""
Wikipedia/Wikimedia APIから各蒸留所の実在する画像URLを取得してdetails.jsonを更新する。
"""
import json
import urllib.request
import urllib.parse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DETAILS_FILE = ROOT / 'data' / 'details.json'
DISTILLERIES_FILE = ROOT / 'data' / 'distilleries.json'

# Distillery id -> Wikipedia page title
# 既存の Wikipedia URL sources から導出
WIKI_TITLE_MAP = {
    'macallan': 'The_Macallan_distillery',
    'ardbeg': 'Ardbeg_distillery',
    'lagavulin': 'Lagavulin_distillery',
    'laphroaig': 'Laphroaig_distillery',
    'glenfiddich': 'Glenfiddich_distillery',
    'glenmorangie': 'Glenmorangie_distillery',
    'talisker': 'Talisker_distillery',
    'highland_park': 'Highland_Park_distillery',
    'bowmore': 'Bowmore_distillery',
    'glenlivet': 'The_Glenlivet_distillery',
    'dalmore': 'Dalmore_distillery',
    'balvenie': 'Balvenie_distillery',
    'aberlour': 'Aberlour_distillery',
    'springbank': 'Springbank_distillery',
    'dalwhinnie': 'Dalwhinnie_distillery',
    'oban': 'Oban_distillery',
    'glenfarclas': 'Glenfarclas_distillery',
    'bunnahabhain': 'Bunnahabhain_distillery',
    'caol_ila': 'Caol_Ila_distillery',
    'bruichladdich': 'Bruichladdich_distillery',
    'kilchoman': 'Kilchoman_distillery',
    'glen_grant': 'Glen_Grant_distillery',
    'glenrothes': 'Glenrothes_Distillery',
    'benromach': 'Benromach_distillery',
    'cardhu': 'Cardhu_distillery',
    'mortlach': 'Mortlach_distillery',
    'cragganmore': 'Cragganmore_distillery',
    'tomatin': 'Tomatin_distillery',
    'glen_moray': 'Glen_Moray_distillery',
    'linkwood': 'Linkwood_distillery',
    'glenallachie': 'Glenallachie_distillery',
    'craigellachie': 'Craigellachie_distillery',
    'clynelish': 'Clynelish_distillery',
    'royal_lochnagar': 'Royal_Lochnagar_distillery',
    'isle_of_jura': 'Jura_distillery',
    'lochranza': 'Arran_distillery',
    'glen_scotia': 'Glen_Scotia_distillery',
    'glenkinchie': 'Glenkinchie_distillery',
    'auchentoshan': 'Auchentoshan_distillery',
    'bladnoch': 'Bladnoch_distillery',
    'deanston': 'Deanston_distillery',
    'aultmore': 'Aultmore_distillery',
    'tobermory': 'Tobermory_distillery',
    'scapa': 'Scapa_distillery',
    'blair_athol': 'Blair_Athol_distillery',
    'pulteney': 'Old_Pulteney_distillery',
    'fettercairn': 'Fettercairn_distillery',
    'teaninich': 'Teaninich_distillery',
    'glen_ord': 'Glen_Ord_distillery',
    'glen_garioch': 'Glen_Garioch_distillery',
    'strathisla': 'Strathisla_distillery',
    'glendronach': 'Glendronach_distillery',
    'ardmore': 'Ardmore_distillery',
    'ardnamurchan': 'Ardnamurchan_distillery',
    'ncnean': "Nc'nean_distillery",
    'wolfburn': 'Wolfburn_distillery',
    'kingsbarns': 'Kingsbarns_distillery',
    'lindores_abbey': 'Lindores_Abbey_distillery',
    'clydeside': 'Clydeside_Distillery',
    'isle_of_raasay': 'Isle_of_Raasay_distillery',
    'torabhaig': 'Torabhaig_distillery',
    'speyburn': 'Speyburn_distillery',
    'knockdhu': 'Knockdhu_distillery',
    'macduff': 'Macduff_distillery',
    'benriach': 'BenRiach_distillery',
    'benrinnes': 'Benrinnes_distillery',
    'royal_brackla': 'Royal_Brackla_distillery',
    'brora': 'Brora_distillery',
    'aberfeldy': 'Aberfeldy_distillery',
    'edradour': 'Edradour_distillery',
    'lagg': 'Lagg_distillery',
    'saxa_vord': 'Saxa_Vord_distillery',
    'holyrood': 'Holyrood_Distillery',
    'port_of_leith': 'Port_of_Leith_distillery',
    'lochlea': 'Lochlea_distillery',
    'dornoch': 'Dornoch_distillery',
    'glendullan': 'Glendullan_distillery',
    'glen_elgin': 'Glen_Elgin_distillery',
    'glenburgie': 'Glenburgie_distillery',
    'glentauchers': 'Glentauchers_distillery',
    'dailuaine': 'Dailuaine_distillery',
    'inchgower': 'Inchgower_distillery',
    'tamdhu': 'Tamdhu_distillery',
    'tomintoul': 'Tomintoul_distillery',
    'miltonduff': 'Miltonduff_distillery',
    'roseisle': 'Roseisle_distillery',
    'balmenach': 'Balmenach_distillery',
    'tamnavulin': 'Tamnavulin_distillery',
    'dufftown': 'Dufftown_distillery',
    'glen_keith': 'Glen_Keith_distillery',
    'knockando': 'Knockando_distillery',
    'port_ellen': 'Port_Ellen_distillery',
    'ballindalloch': 'Ballindalloch_distillery',
    'mannochmore': 'Mannochmore_distillery',
    'glenlossie': 'Glenlossie_distillery',
    'auchroisk': 'Auchroisk_distillery',
    'kininvie': 'Kininvie_distillery',
    'strathmill': 'Strathmill_distillery',
    'glen_spey': 'Glen_Spey_distillery',
    'glengyle': 'Glengyle_distillery',
    'daftmill': 'Daftmill_distillery',
    'ailsa_bay': 'Ailsa_Bay_distillery',
    'annandale': 'Annandale_distillery',
    'inchdairnie': 'Inchdairnie_distillery',
    'dalmunach': 'Dalmunach_distillery',
    'braeval': 'Braeval_distillery',
    'allt_a_bhainne': 'Allt-A-Bhainne_distillery',
    'arbikie': 'Arbikie_distillery',
    'glasgow': 'Glasgow_distillery',
    'isle_of_harris': 'Isle_of_Harris_Distillery',
    'bonnington': 'Bonnington_distillery',
    'ardnahoe': 'Ardnahoe_distillery',
    'tullibardine': 'Tullibardine_distillery',
    'glenwyvis': 'GlenWyvis_distillery',
    'aberargie': 'Aberargie_distillery',
    'strathearn': 'Strathearn_distillery',
    'borders': 'Borders_distillery',
    'ardross': 'Ardross_distillery',
    'dunphail': 'Dunphail_distillery',
    'falkirk': 'Falkirk_distillery',
    'ardgowan': 'Ardgowan_distillery',
}


def get_page_image(title):
    """Wikipedia pageimages APIから画像URLを取得"""
    url = ('https://en.wikipedia.org/w/api.php?'
           + urllib.parse.urlencode({
               'action': 'query',
               'titles': title,
               'prop': 'pageimages',
               'format': 'json',
               'pithumbsize': '800',
               'piprop': 'thumbnail|name|original',
           }))
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'WhiskyMap/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        pages = data.get('query', {}).get('pages', {})
        for pid, page in pages.items():
            if pid == '-1':
                return None
            thumb = page.get('thumbnail', {}).get('source')
            original = page.get('original', {}).get('source')
            return thumb or original
    except Exception as e:
        print(f'  ERROR: {title}: {e}', file=sys.stderr)
    return None


def main():
    with open(DETAILS_FILE, encoding='utf-8') as f:
        details = json.load(f)
    updated = 0
    missing = []
    for did, title in WIKI_TITLE_MAP.items():
        if did not in details:
            continue
        img = get_page_image(title)
        if img:
            details[did]['image'] = img
            updated += 1
            print(f'  OK  {did}: {img}')
        else:
            missing.append((did, title))
            print(f'  NG  {did}: {title}')
        time.sleep(0.3)
    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print(f'\n{updated} images updated, {len(missing)} not found')
    for did, t in missing:
        print(f'  - {did}: {t}')


if __name__ == '__main__':
    main()
