#!/usr/bin/env python
"""mom_results.json の結果を details.json に適用 - 既存ボトル名と最良マッチ"""
import json
import re
from pathlib import Path
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parent.parent
DETAILS_FILE = ROOT / 'data' / 'details.json'
MOM_FILE = ROOT / 'scripts' / 'mom_results.json'


def normalize(s):
    s = s.lower()
    s = re.sub(r'\([^)]*\)', '', s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def best_match(target, candidates, threshold=0.4):
    """Find best matching candidate by name similarity"""
    target_n = normalize(target)
    best, best_score = None, 0
    for c in candidates:
        c_n = normalize(c['name'])
        # Custom scoring: word overlap + sequence similarity
        target_words = set(target_n.split())
        cand_words = set(c_n.split())
        overlap = len(target_words & cand_words) / max(len(target_words), 1)
        seq = SequenceMatcher(None, target_n, c_n).ratio()
        score = (overlap * 0.6) + (seq * 0.4)
        if score > best_score:
            best, best_score = c, score
    return (best, best_score) if best_score >= threshold else (None, best_score)


def main():
    with open(DETAILS_FILE, encoding='utf-8') as f:
        details = json.load(f)
    with open(MOM_FILE, encoding='utf-8') as f:
        mom = json.load(f)
    retry_path = ROOT / 'scripts' / 'mom_retry_results.json'
    if retry_path.exists():
        with open(retry_path, encoding='utf-8') as f:
            retry = json.load(f)
            mom.update(retry)
    search_path = ROOT / 'scripts' / 'mom_search_results.json'
    if search_path.exists():
        with open(search_path, encoding='utf-8') as f:
            srch = json.load(f)
            for k, v in srch.items():
                if k not in mom:
                    mom[k] = v
                else:
                    mom[k].extend(v)

    applied = 0
    replaced_ext = 0
    replaced_rep = 0
    new_added = 0
    skip_real = 0
    for did, products in mom.items():
        if did not in details or not products:
            continue
        for section in ('core', 'limited'):
            bottles = details[did].get('bottles', {}).get(section, [])
            for b in bottles:
                # Skip if already has real (non-fallback) bottle image
                if b.get('image') and not b.get('_is_rep') and not b.get('_is_exterior'):
                    skip_real += 1
                    continue
                # Find best match in MoM products
                match, score = best_match(b['name'], products, threshold=0.35)
                if match:
                    was_ext = b.get('_is_exterior', False)
                    was_rep = b.get('_is_rep', False)
                    b['image'] = match['image']
                    b['_mom_match'] = match['name']
                    b.pop('_is_exterior', None)
                    b.pop('_is_rep', None)
                    applied += 1
                    if was_ext: replaced_ext += 1
                    elif was_rep: replaced_rep += 1
                    else: new_added += 1
    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)

    # Stats
    total = 0
    real = 0
    rep = 0
    ext = 0
    for did, data in details.items():
        if did.startswith('_'): continue
        for s in ('core','limited'):
            for b in data.get('bottles', {}).get(s, []):
                total += 1
                if b.get('image'):
                    if b.get('_is_exterior'): ext += 1
                    elif b.get('_is_rep'): rep += 1
                    else: real += 1
    print(f'Applied: {applied} (replaced exterior: {replaced_ext}, replaced rep: {replaced_rep}, new: {new_added})')
    print(f'Skipped (already real): {skip_real}')
    print(f'Final: Real {real}, Rep {rep}, Exterior {ext} = {real+rep+ext}/{total}')


if __name__ == '__main__':
    main()
