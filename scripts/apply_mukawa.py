#!/usr/bin/env python
"""武川蒸留酒販売の検索結果からボトル画像をdetails.jsonに適用。
   蒸留所固有のキーワードでフィルタしてマッチを高精度化。"""
import json
import re
from pathlib import Path
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parent.parent
DETAILS_FILE = ROOT / 'data' / 'details.json'
COMPACT = ROOT / 'scripts' / 'mw_compact.txt'

# Distillery → Japanese name patterns it MUST contain (filter out unrelated products)
NAME_FILTER = {
    'lochlea': ['ロッホリー'],
    'lagg': ['ラグ', 'キルモリー', 'コーリエクラビー'],
    'glasgow': ['グラスゴー', '1770'],
    'clydeside': ['クライドサイド', 'ストブクロス'],
    'isle_of_raasay': ['ラッセイ', 'ナ シア'],
    'torabhaig': ['トラベイグ', 'アルト グレン'],
    'ardnamurchan': ['アードナマッカン', 'アードナムッカン', 'AD/'],
    'ncnean': ['ノックニーアン', 'クワイエット', 'ハントレス'],
    'saxa_vord': ['サクサ', 'ヴォード', 'シェットランド リール'],
    'port_of_leith': ['ポート オブ リース', 'ポートオブリース'],
    'borders': ['ボーダーズ蒸留所', 'ボーダーズ', 'スコッチ ホリデイ', 'クラン フレイザー', 'ロウアー イースト サイド'],
    'falkirk': ['ファルカーク蒸留所', 'ファルカーク 蒸留', 'ファルカーク シングル'],
    'aberargie': ['アベラーギ'],
    'dunphail': ['ダンフェイル'],
    'cabrach': ['カブラック', 'ザ カブラック'],
    'dalmunach': ['ダルムナック'],
    'roseisle': ['ローズアイル'],
    'bonnington': ['ボニントン'],
    'ardross': ['アードロス'],
    'ardgowan': ['アードゴーワン'],
    'uilebheist': ['ユーレビースト', 'ユーリ'],
    'inchdairnie': ['インチデアニー'],
    'annandale': ['アナンデール'],
    'arbikie': ['アービッキー'],
    'glenwyvis': ['グレンウィヴィス', 'グレン ウィヴィス'],
    'glengyle': ['キルケラン', 'グレンガイル'],
    'wolfburn': ['ウルフバーン'],
    'kingsbarns': ['キングスバーンズ'],
    'holyrood': ['ホーリールード'],
    'lindores_abbey': ['リンドアズ', 'リンドーズ'],
    'ailsa_bay': ['アイルサ ベイ', 'アイルサベイ'],
    'aerstone': ['エアストーン'],
    'speyburn': ['スペイバーン'],
    'kininvie': ['キニンヴィ'],
    'tullibardine': ['タリバーディン'],
    'glen_ord': ['シングルトン グレンオード', 'シングルトン オブ グレンオード', 'グレンオード'],
    'glen_keith': ['グレンキース'],
    'glentauchers': ['グレントファース', 'グレントーチャーズ'],
    'dailuaine': ['ダルユーイン', 'ダルウィーン'],
    'inchgower': ['インチガワー'],
    'teaninich': ['ティーニニック'],
    'mannochmore': ['マノックモア'],
    'glenlossie': ['グレンロッシー'],
    'auchroisk': ['オスロスク', 'シングルトン オブ オスロスク'],
    'strathmill': ['ストラスミル'],
    'glen_spey': ['グレンスペイ'],
    'miltonduff': ['ミルトンダフ'],
    'balmenach': ['バルメナック', 'カオルン'],
    'glenburgie': ['グレンバーギ'],
    'allt_a_bhainne': ['アルトベーン', 'アルト ア ベーン'],
    'daftmill': ['ダフトミル'],
}

# Reject patterns (other distilleries that share search terms)
REJECT = [
    'ブレアソール',  # Blair Athol
    'モンバッチョ',  # Mombacho rum
    'アハトロ',  # Ahatro tequila
    'キングスバリー',  # Kingsbury (independent bottler)
    'アイランド シグネチャー',
    'スケープグレース',  # Scapegrace gin
    'ベルヴェデール',  # Belvedere vodka
    'フロール デ カーニャ',
    'ハイボール エクスプレス',
    'ウエストランド',
    'ウイスキーコンチェルト',
    'ボタニスト',  # Botanist gin
    'スターワード',  # Starward
    'ドーノッホ',  # Dornoch (separate)
    'BB&R',  # Berry Bros
    'フェイブル',  # Fable
]


def is_relevant(name, did):
    """Check if a product name matches the target distillery"""
    patterns = NAME_FILTER.get(did, [])
    if not patterns:
        return False
    name_n = name.replace('　', ' ').replace(' ', '')
    # Reject if contains another distillery name
    for r in REJECT:
        if r.replace('　', '').replace(' ', '') in name_n:
            # But allow if it ALSO matches our distillery
            for p in patterns:
                if p.replace('　', '').replace(' ', '') in name_n and len(p) > 4:
                    break
            else:
                return False
    # Must match at least one pattern
    for p in patterns:
        if p.replace('　', '').replace(' ', '') in name_n:
            return True
    return False


def best_match(target, candidates, threshold=0.3):
    """Find best matching candidate by name similarity (Japanese-aware)"""
    target_n = target.lower().replace('　', '').replace(' ', '')
    # Strip parenthetical descriptions
    target_n = re.sub(r'\([^)]*\)', '', target_n)
    target_n = re.sub(r'[^a-z0-9ぁ-んァ-ヶー]', '', target_n)
    best, best_score = None, 0
    for c in candidates:
        c_n = c['name'].lower().replace('　', '').replace(' ', '')
        c_n = re.sub(r'\([^)]*\)', '', c_n)
        c_n = re.sub(r'[^a-z0-9ぁ-んァ-ヶー]', '', c_n)
        seq = SequenceMatcher(None, target_n, c_n).ratio()
        # Boost if target keywords appear in candidate
        target_words = re.findall(r'[ァ-ヶー]+|[a-z0-9]+', target.lower())
        cand_words = re.findall(r'[ァ-ヶー]+|[a-z0-9]+', c['name'].lower())
        word_match = sum(1 for w in target_words if any(w in cw for cw in cand_words)) / max(len(target_words), 1)
        score = seq * 0.4 + word_match * 0.6
        if score > best_score:
            best, best_score = c, score
    return (best, best_score) if best_score >= threshold else (None, best_score)


def main():
    # Load compact data
    products_by_dist = {}
    for line in COMPACT.read_text(encoding='utf-8').splitlines():
        parts = line.split('|', 4)
        if len(parts) < 4:
            continue
        did, pid, ext, name = parts[0], parts[1], parts[2], parts[3]
        memo = parts[4] if len(parts) >= 5 else ''
        ext_full = 'png' if ext == 'p' else 'jpg'
        image = f'https://img07.shop-pro.jp/PA01356/240/product/{pid}_th.{ext_full}'
        # Filter by relevance
        if is_relevant(name, did):
            products_by_dist.setdefault(did, []).append({'name': name, 'image': image, 'memo': memo})

    print('Filtered products per distillery:')
    for did, plist in sorted(products_by_dist.items()):
        print(f'  {did}: {len(plist)}')

    # Apply to details.json
    with open(DETAILS_FILE, encoding='utf-8') as f:
        details = json.load(f)

    applied = 0
    replaced_ext = 0
    replaced_rep = 0

    for did, products in products_by_dist.items():
        if did not in details or not products:
            continue
        # Pick the most "core-looking" product as the representative real bottle
        # Prefer products without "並行" (parallel import suffix), prefer shortest name
        sorted_p = sorted(products, key=lambda p: (
            '並行' in p['name'],
            len(p['name'])
        ))
        rep_product = sorted_p[0]
        for section in ('core', 'limited'):
            bottles = details[did].get('bottles', {}).get(section, [])
            for b in bottles:
                # Skip if has real bottle image (non-fallback)
                if b.get('image') and not b.get('_is_rep') and not b.get('_is_exterior'):
                    continue
                # Try exact-ish match first
                match, score = best_match(b['name'], products, threshold=0.25)
                # Otherwise fall back to representative product
                use_match = match if match else rep_product
                use_as_rep = match is None
                was_ext = b.get('_is_exterior', False)
                was_rep = b.get('_is_rep', False)
                b['image'] = use_match['image']
                b['_mukawa_match'] = use_match['name'][:60]
                if use_as_rep:
                    b['_is_rep'] = True
                else:
                    b.pop('_is_rep', None)
                b.pop('_is_exterior', None)
                applied += 1
                if was_ext: replaced_ext += 1
                elif was_rep: replaced_rep += 1

    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)

    print(f'\nApplied {applied} (replaced exterior: {replaced_ext}, rep: {replaced_rep})')

    # Stats
    total = real = rep = ext = 0
    for did, data in details.items():
        if did.startswith('_'): continue
        for s in ('core', 'limited'):
            for b in data.get('bottles', {}).get(s, []):
                total += 1
                if b.get('image'):
                    if b.get('_is_exterior'): ext += 1
                    elif b.get('_is_rep'): rep += 1
                    else: real += 1
    print(f'Final: Real {real}, Rep {rep}, Exterior {ext} = {real+rep+ext}/{total}')


if __name__ == '__main__':
    main()
