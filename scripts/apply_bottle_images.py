#!/usr/bin/env python
"""
Chunk 1/2a/2c の結果をdetails.jsonに適用。
蒸留所固有コード(例: abgob=Ardbeg)を検証してmismatchを除外。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DETAILS_FILE = ROOT / 'data' / 'details.json'

# Distillery-specific TWE codes (prefix in filename)
# These codes are unique per distillery; matching them confirms the bottle
DISTILLERY_CODES = {
    'macallan': ['macob', 'mac_', 'macsig', 'macg', 'maccd'],
    'ardbeg': ['abgob', 'abg_', 'abgsig', 'abgg'],
    'lagavulin': ['lgvob', 'lgvsig', 'lgvcd', 'lgvg'],
    'laphroaig': ['lrgob', 'lrged', 'lrgsig', 'lrgcd', 'lrgg', 'lrgksp'],
    'glenfiddich': ['gfdob', 'gfdsig', 'gfdcd'],
    'glenmorangie': ['gmgob', 'gmgsig', 'gmgcd'],
    'talisker': ['talob', 'talsig', 'talcd', 'talg'],
    'highland_park': ['hlpob', 'hlpsig', 'hlpcd'],
    'bowmore': ['bowob', 'bow_', 'bowsig', 'bowcd'],
    'glenlivet': ['glvob', 'glvsig', 'glvcd'],
    'dalmore': ['dlmob', 'dlmsig', 'dlmcd'],
    'balvenie': ['balob', 'balsig', 'balcd'],
    'aberlour': ['ablob', 'ablsig', 'ablcd'],
    'springbank': ['sprob', 'sprsig', 'sprcd', 'sets_spr', 'lgrob', 'hazob'],  # Longrow/Hazelburn share
    'dalwhinnie': ['dalob', 'dalsig', 'dalcd'],
    'glenfarclas': ['gfcob', 'gfcsig', 'gfccd'],
    'bunnahabhain': ['bunob', 'bunsig', 'buncd'],
    'caol_ila': ['cilob', 'cilsig', 'cilcd'],
    'bruichladdich': ['bruob', 'pclob', 'octob'],  # Port Charlotte/Octomore
    'kilchoman': ['kilob', 'kilsig'],
    'glen_grant': ['ggtob', 'ggtind', 'ggtsig', 'ggtcd'],
    'glenrothes': ['grsob', 'grsdt', 'grstho', 'grscd'],
    'benromach': ['brmob', 'bnrob', 'brmsig'],  # bnrob is Benromach variant
    'cardhu': ['carob', 'carsig'],
    'mortlach': ['mtlob', 'mtlsig'],
    'cragganmore': ['cgmob', 'cgmsig'],
    'tomatin': ['tomob', 'tomsig', 'mini_sm_tom'],
    'glen_moray': ['gmyob', 'gmysig', 'mini_sm_gmy'],
    'linkwood': ['lkwob', 'lkwsig'],
    'glenallachie': ['gleob', 'glesig', 'mini_sm_gle'],
    'craigellachie': ['crgob', 'crgsig'],
    'clynelish': ['clyob', 'clysig', 'clyg', 'clyrm'],
    'royal_lochnagar': ['rlnob', 'rlnsig', 'rlnrm'],
    'isle_of_jura': ['iojob', 'iojsig', 'mini_sm_ioj'],
    'lochranza': ['arrob', 'arrsig'],
    'glen_scotia': ['gstob', 'gstsig'],
    'glenkinchie': ['gkcob', 'gkcsig'],
    'auchentoshan': ['aucob', 'aucsig', 'aucddm'],
    'bladnoch': ['bdnob', 'bdnsig'],
    'deanston': ['dstob', 'dstsig', 'mini_sm_dst'],
    'aultmore': ['aulob', 'aulsig', 'aulrm'],
    'tobermory': ['tobob', 'tobsig', 'ldgob'],  # Ledaig
    'scapa': ['scpob', 'scpsig'],
    'blair_athol': ['blaob', 'blasig', 'blafe'],
    'pulteney': ['opnob', 'opncd'],
    'fettercairn': ['ofcob', 'ofcsig'],
    'glen_garioch': ['ggrob', 'ggred', 'mini_sm_ggr'],
    'strathisla': ['stlob', 'stlcd', 'stlg'],
    'glendronach': ['grnob', 'grnsig'],
    'ardmore': ['ardob', 'ardsig'],
    'ardnamurchan': ['amcob', 'amcsig'],
    'wolfburn': ['wolob', 'wolsig'],  # cauldron results were wrong, won't match
    'kingsbarns': ['kgbob', 'kgbsig'],
    'benriach': ['bnrob', 'bnrsig', 'mini_sm_bnr'],
    'benrinnes': ['brnob', 'brnsig'],
    'royal_brackla': ['rblob', 'rblsig'],
    'strathearn': ['senop', 'sesig'],  # Strathearn ENOP
    'glengyle': ['klkob', 'klksig'],  # Kilkerran
    'daftmill': ['dafob', 'dafsig'],
    'ailsa_bay': ['aisob', 'aissig'],
    'annandale': ['annob', 'annsig'],
    'tamnavulin': ['tmnob', 'tmnsig'],
    'dufftown': ['dufob', 'dufsig'],
    'tamdhu': ['tamob', 'tamsig', 'pm_tamob'],
    'tomintoul': ['tmtob', 'tmtsig', 'mini_sm_tmt', 'bltob'],  # bltob = Ballantruan
    'aberfeldy': ['abfob', 'abfsig', 'mini_sm_abf'],
    'edradour': ['edrob', 'edrsig', 'blcob', 'mini_sm_blc'],  # Ballechin
    'knockdhu': ['ancob', 'ancsig'],  # anCnoc
    'macduff': ['gdrob', 'gdrsig'],  # Glen Deveron
    'oban': ['obnob', 'obnsig'],
}


def is_valid_match(did, filename):
    """Check if filename code matches the distillery"""
    codes = DISTILLERY_CODES.get(did, [])
    lower = filename.lower()
    return any(lower.startswith(c) for c in codes)


def main():
    # Parse result files
    results = {}
    for f in ['twe_chunk1_results.txt', 'twe_chunk2a_results.txt', 'twe_chunk2c_results.txt']:
        path = ROOT / 'scripts' / f
        if not path.exists():
            continue
        for line in path.read_text(encoding='utf-8').splitlines():
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            if k in results:
                continue  # Earlier chunks take precedence? No, later chunks have better DOM parsing. Prefer later.
            results[k] = v.strip()
    # Also re-parse to prefer chunk 2 (DOM parsed) over chunk 1 (regex)
    # Re-scan chunks and override with later ones
    results = {}
    for f in ['twe_chunk1_results.txt', 'twe_chunk2a_results.txt', 'twe_chunk2c_results.txt']:
        path = ROOT / 'scripts' / f
        if not path.exists():
            continue
        for line in path.read_text(encoding='utf-8').splitlines():
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            results[k] = v.strip()  # Later overrides earlier

    print(f'Total raw results: {len(results)}')
    # Apply filter
    applied = 0
    rejected = 0
    with open(DETAILS_FILE, encoding='utf-8') as f:
        details = json.load(f)
    for key, slug in results.items():
        parts = key.split('|')
        if len(parts) != 3:
            continue
        did, section, idx = parts[0], parts[1], int(parts[2])
        if did not in details:
            continue
        if section not in details[did].get('bottles', {}):
            continue
        bottles = details[did]['bottles'][section]
        if idx >= len(bottles):
            continue
        # Skip if already has image
        if bottles[idx].get('image'):
            continue
        # Extract filename
        filename = slug.split('/')[-1] if '/' in slug else slug
        if not is_valid_match(did, filename):
            rejected += 1
            continue
        # Build URL
        url = 'https://img.thewhiskyexchange.com/' + (slug if '/' in slug else '380/' + slug)
        bottles[idx]['image'] = url
        applied += 1
    print(f'Applied: {applied}, Rejected: {rejected}')
    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    # Stats
    total_bottles = 0
    with_img = 0
    for did, data in details.items():
        if did.startswith('_'): continue
        for s in ('core', 'limited'):
            for b in data.get('bottles', {}).get(s, []):
                total_bottles += 1
                if b.get('image'):
                    with_img += 1
    print(f'Total bottles: {total_bottles}, with image: {with_img} ({with_img*100//total_bottles}%)')


if __name__ == '__main__':
    main()
