#!/usr/bin/env python
"""
The Whisky Exchangeから全ボトルの画像URLを取得。
Browser User-Agentを使用。
"""
import json
import urllib.request
import urllib.parse
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DETAILS_FILE = ROOT / 'data' / 'details.json'

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode('utf-8', errors='ignore')


def search_twe(query):
    """Search The Whisky Exchange and return first bottle image URL."""
    url = 'https://www.thewhiskyexchange.com/search?q=' + urllib.parse.quote(query)
    try:
        html = fetch(url)
    except Exception as e:
        print(f'  search err: {e}', file=sys.stderr)
        return None
    # Look for first product image from img.thewhiskyexchange.com
    m = re.search(r'https://img\.thewhiskyexchange\.com/\d+/[a-z0-9_.\-]+\.(?:jpg|png|webp)(?:\?v=\d+)?', html, re.IGNORECASE)
    if m:
        return m.group(0)
    return None


def clean_bottle_name(name):
    # Remove parenthetical Japanese descriptions
    name = re.sub(r'\([^)]*[^\x00-\x7f][^)]*\)', '', name)
    # Remove ABV info like "(40%)"
    name = re.sub(r'\(\d+%?\)', '', name)
    # Remove parenthetical English annotations like "(NAS)", "(CS)"
    name = re.sub(r'\((?:NAS|CS|毎年|バッチ毎|限定|常売)\)', '', name, flags=re.IGNORECASE)
    return name.strip()


def main():
    with open(DETAILS_FILE, encoding='utf-8') as f:
        details = json.load(f)
    # Build task list
    tasks = []
    for did, data in details.items():
        if did.startswith('_'):
            continue
        name_en = did.replace('_', ' ')
        # Use distillery name from data if available
        for section in ('core', 'limited'):
            for i, bottle in enumerate(data.get('bottles', {}).get(section, [])):
                if bottle.get('image'):
                    continue
                tasks.append((did, section, i, bottle['name']))
    print(f'Total bottles to fetch: {len(tasks)}', file=sys.stderr)
    updated = 0
    failed = 0
    # Map did to display name
    dist_display = {
        'macallan': 'Macallan', 'ardbeg': 'Ardbeg', 'lagavulin': 'Lagavulin',
        'laphroaig': 'Laphroaig', 'glenfiddich': 'Glenfiddich',
        'glenmorangie': 'Glenmorangie', 'talisker': 'Talisker',
        'highland_park': 'Highland Park', 'bowmore': 'Bowmore',
        'glenlivet': 'Glenlivet', 'dalmore': 'Dalmore', 'balvenie': 'Balvenie',
        'aberlour': 'Aberlour', 'springbank': 'Springbank',
        'dalwhinnie': 'Dalwhinnie', 'oban': 'Oban', 'glenfarclas': 'Glenfarclas',
        'bunnahabhain': 'Bunnahabhain', 'caol_ila': 'Caol Ila',
        'bruichladdich': 'Bruichladdich', 'kilchoman': 'Kilchoman',
        'glen_grant': 'Glen Grant', 'glenrothes': 'Glenrothes',
        'benromach': 'Benromach', 'cardhu': 'Cardhu',
        'mortlach': 'Mortlach', 'cragganmore': 'Cragganmore',
        'tomatin': 'Tomatin', 'glen_moray': 'Glen Moray',
        'linkwood': 'Linkwood', 'glenallachie': 'GlenAllachie',
        'craigellachie': 'Craigellachie', 'clynelish': 'Clynelish',
        'royal_lochnagar': 'Royal Lochnagar', 'isle_of_jura': 'Jura',
        'lochranza': 'Arran', 'glen_scotia': 'Glen Scotia',
        'glenkinchie': 'Glenkinchie', 'auchentoshan': 'Auchentoshan',
        'bladnoch': 'Bladnoch', 'deanston': 'Deanston',
        'aultmore': 'Aultmore', 'tobermory': 'Tobermory',
        'scapa': 'Scapa', 'blair_athol': 'Blair Athol',
        'pulteney': 'Old Pulteney', 'fettercairn': 'Fettercairn',
        'teaninich': 'Teaninich', 'glen_ord': 'Singleton of Glen Ord',
        'glen_garioch': 'Glen Garioch', 'strathisla': 'Strathisla',
        'glendronach': 'GlenDronach', 'ardmore': 'Ardmore',
        'ardnamurchan': 'Ardnamurchan', 'ncnean': "Nc'nean",
        'wolfburn': 'Wolfburn', 'kingsbarns': 'Kingsbarns',
        'lindores_abbey': 'Lindores Abbey', 'clydeside': 'Clydeside',
        'isle_of_raasay': 'Raasay', 'torabhaig': 'Torabhaig',
        'speyburn': 'Speyburn', 'knockdhu': 'anCnoc',
        'macduff': 'Deveron', 'benriach': 'BenRiach',
        'benrinnes': 'Benrinnes', 'royal_brackla': 'Royal Brackla',
        'brora': 'Brora', 'aberfeldy': 'Aberfeldy',
        'edradour': 'Edradour', 'lagg': 'Lagg',
        'saxa_vord': 'Shetland Reel', 'holyrood': 'Holyrood',
        'port_of_leith': 'Port of Leith', 'lochlea': 'Lochlea',
        'dornoch': 'Dornoch', 'glendullan': 'Singleton of Glendullan',
        'glen_elgin': 'Glen Elgin', 'glenburgie': 'Glenburgie',
        'glentauchers': 'Glentauchers', 'dailuaine': 'Dailuaine',
        'inchgower': 'Inchgower', 'tamdhu': 'Tamdhu',
        'tomintoul': 'Tomintoul', 'miltonduff': 'Miltonduff',
        'roseisle': 'Roseisle', 'balmenach': 'Balmenach',
        'tamnavulin': 'Tamnavulin', 'dufftown': 'Singleton of Dufftown',
        'glen_keith': 'Glen Keith', 'knockando': 'Knockando',
        'port_ellen': 'Port Ellen', 'ballindalloch': 'Ballindalloch',
        'mannochmore': 'Mannochmore', 'glenlossie': 'Glenlossie',
        'auchroisk': 'Auchroisk', 'kininvie': 'Kininvie',
        'strathmill': 'Strathmill', 'glen_spey': 'Glen Spey',
        'glengyle': 'Kilkerran', 'daftmill': 'Daftmill',
        'ailsa_bay': 'Ailsa Bay', 'annandale': 'Annandale',
        'inchdairnie': 'InchDairnie', 'dalmunach': 'Dalmunach',
        'braeval': 'Braeval', 'allt_a_bhainne': 'Allt-a-Bhainne',
        'arbikie': 'Arbikie', 'glasgow': 'Glasgow 1770',
        'isle_of_harris': 'Harris', 'bonnington': 'Bonnington',
        'ardnahoe': 'Ardnahoe', 'tullibardine': 'Tullibardine',
        'glenwyvis': 'GlenWyvis', 'aberargie': 'Aberargie',
        'strathearn': 'Strathearn', 'borders': 'Borders',
        'ardross': 'Ardross', 'dunphail': 'Dunphail',
        'falkirk': 'Falkirk', 'ardgowan': 'Ardgowan',
        'cabrach': 'Cabrach', 'uilebheist': 'Uile-bheist',
    }
    for did, section, idx, bname in tasks:
        dname = dist_display.get(did, did.replace('_', ' ').title())
        clean = clean_bottle_name(bname)
        # If bottle name already contains distillery, don't duplicate
        query = clean if dname.lower() in clean.lower() else f'{dname} {clean}'
        # Limit query length
        query = ' '.join(query.split()[:5])  # max 5 words
        img = search_twe(query)
        if img:
            details[did]['bottles'][section][idx]['image'] = img
            updated += 1
            if updated % 20 == 0:
                print(f'  [{updated}] {did} "{bname[:25]}" -> {img.split("/")[-1][:30]}', file=sys.stderr)
        else:
            failed += 1
        time.sleep(0.4)  # Rate limit respect
    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print(f'\nUpdated: {updated}, Failed: {failed}', file=sys.stderr)


if __name__ == '__main__':
    main()
