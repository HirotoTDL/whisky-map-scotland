#!/usr/bin/env python
"""
ボトル画像のない箇所に、同じ蒸留所の利用可能な画像で補填。
フラッグシップ→常売→限定の優先度で選ぶ。
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
        # Collect available images from core first, then limited
        rep_images = []
        for section in ('core', 'limited'):
            for b in data.get('bottles', {}).get(section, []):
                if b.get('image') and not b.get('_is_rep'):
                    rep_images.append(b['image'])
        if not rep_images:
            continue
        # Use first image as fallback
        fallback = rep_images[0]
        # Apply to missing bottles
        for section in ('core', 'limited'):
            for b in data.get('bottles', {}).get(section, []):
                if not b.get('image'):
                    b['image'] = fallback
                    b['_is_rep'] = True  # Mark as representative image
                    filled += 1

    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)

    # Stats
    total = 0
    with_img = 0
    real = 0
    rep = 0
    for did, data in details.items():
        if did.startswith('_'): continue
        for s in ('core','limited'):
            for b in data.get('bottles', {}).get(s, []):
                total += 1
                if b.get('image'):
                    with_img += 1
                    if b.get('_is_rep'):
                        rep += 1
                    else:
                        real += 1
    print(f'Filled with rep: {filled}')
    print(f'Total bottles: {total}')
    print(f'Real images: {real}')
    print(f'Rep images: {rep}')
    print(f'With any image: {with_img}/{total} ({with_img*100//total}%)')


if __name__ == '__main__':
    main()
