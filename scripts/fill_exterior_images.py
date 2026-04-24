#!/usr/bin/env python
"""
ボトル画像が1本もない蒸留所に、蒸留所外観画像をフォールバック。
視覚的参照のため、蒸留所イメージで統一する。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DETAILS_FILE = ROOT / 'data' / 'details.json'


def main():
    with open(DETAILS_FILE, encoding='utf-8') as f:
        details = json.load(f)

    filled = 0
    for did, data in details.items():
        if did.startswith('_'):
            continue
        # Check if distillery has NO bottle images
        has_any_bottle = False
        for s in ('core','limited'):
            for b in data.get('bottles', {}).get(s, []):
                if b.get('image'):
                    has_any_bottle = True
                    break
            if has_any_bottle: break
        if has_any_bottle:
            continue
        # Use exterior image
        ext_img = data.get('image')
        if not ext_img:
            continue
        # Apply to all bottles
        for s in ('core','limited'):
            for b in data.get('bottles', {}).get(s, []):
                if not b.get('image'):
                    b['image'] = ext_img
                    b['_is_exterior'] = True
                    filled += 1

    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)

    # Stats
    total = 0
    with_img = 0
    real = 0
    rep = 0
    ext = 0
    for did, data in details.items():
        if did.startswith('_'): continue
        for s in ('core','limited'):
            for b in data.get('bottles', {}).get(s, []):
                total += 1
                if b.get('image'):
                    with_img += 1
                    if b.get('_is_exterior'):
                        ext += 1
                    elif b.get('_is_rep'):
                        rep += 1
                    else:
                        real += 1
    print(f'Filled exterior: {filled}')
    print(f'Real: {real}, Rep: {rep}, Exterior: {ext}')
    print(f'Coverage: {with_img}/{total} ({with_img*100//total}%)')


if __name__ == '__main__':
    main()
