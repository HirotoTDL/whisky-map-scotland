#!/usr/bin/env python
"""残り42蒸留所の詳細データを追加"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DETAILS_FILE = ROOT / 'data' / 'details.json'

# Helper: build empty bottle list
def NB(*names, types=None):
    """Names → list of bottle dicts with empty image"""
    if types is None:
        types = ['常売'] * len(names)
    return [{'name': n, 'type': t, 'image': ''} for n, t in zip(names, types)]

ENTRIES = {
    # === Highland - Active Established ===
    'brewdog': {
        'characteristics': 'アバディーンシャー、エロン。クラフトビール大手BrewDog plcが2018年に開設したLone Wolf Distillery(統合運営)。年産5万L、Diageo由来の中古スチル使用。シングルモルト"Lone Wolf"とジン/ラム/ウォッカも生産。マーケティング先行のクラフト系。',
        'signature': {'name': 'Lone Wolf Single Malt (NAS)', 'cask': 'バーボン樽+ヘビートースト・ヴァージンオーク', 'color': 'ペールゴールド', 'taste': '若々しいバニラ、軽いスパイス、シリアル、フレッシュなクラフトハイランド'},
        'bottles': {'core': NB('Lone Wolf Single Malt (NAS)', 'Lone Wolf Cloudy Lemon Gin', 'Lone Wolf Vodka'), 'limited': NB('Lone Wolf Cask Strength', 'BrewDog Distillery Edition')}
    },
    'burn_obennie': {
        'characteristics': '東ハイランド、アバディーンシャー、バンチョリー近郊。2019年Deeside Distillery創業。年産1万L超のマイクロ蒸留所。シングルモルトはまだ熟成中で、ジン/ラムが先行販売。',
        'signature': {'name': 'Burn O\' Bennie Single Malt (熟成中、2025〜予定)', 'cask': 'バーボン樽+シェリー樽', 'color': '—', 'taste': '—'},
        'bottles': {'core': NB('Deeside Aldie Castle Gin', 'Deeside Pollybank Rum'), 'limited': NB('Burn O\' Bennie New Make', 'Founders Cask')}
    },
    '8doors': {
        'characteristics': '北ハイランド、ジョン・オ・グローツ、スコットランド本土最北東。2022年Morrison家族創業。"8 Doors"は地元ホテルにあった伝説の8つの扉に由来。スチル1対、年産10万L。新進気鋭のマイクロ。',
        'signature': {'name': '8 Doors Single Malt (熟成中、2025〜予定)', 'cask': 'バーボン樽+シェリー樽', 'color': '—', 'taste': '—'},
        'bottles': {'core': NB('8 Doors New Make Spirit', 'Founders Cask Programme'), 'limited': NB('Inaugural Release (予定)')}
    },
    'persie': {
        'characteristics': '南ハイランド、パースシャー、ブリッジ・オブ・カリー。2015年創業のクラフト蒸留所。Persieはジン主体だがシングルモルトも蒸留。',
        'signature': {'name': 'Persie Wilderness Single Malt', 'cask': 'バーボン樽', 'color': 'ペールゴールド', 'taste': '蜂蜜、フローラル、軽いシリアル、ハイランドのエレガントさ'},
        'bottles': {'core': NB('Persie Sweetheart Gin', 'Persie Herby & Aromatic Gin', 'Persie Wilderness Single Malt'), 'limited': NB('Persie Single Cask')}
    },
    'speyside': {
        'characteristics': 'ハイランド/スペイサイド境界、キンガッシー近郊。1990年George Christie氏創業、Speyside Distillers Co.所有。Spey/Drumguish銘柄で展開。スチル1対、年産60万L。',
        'signature': {'name': 'Spey Tenné', 'cask': 'バーボン樽+ポート樽フィニッシュ', 'color': 'ディープゴールド', 'taste': 'フルーツケーキ、ハニー、ポートの甘さ、スパイス'},
        'bottles': {'core': NB('Spey Tenné', 'Spey Trutina', 'Spey 12 Year Old', 'Spey 18 Year Old', 'Drumguish (NAS)'), 'limited': NB('Spey 25 / 30', 'Spey Cask Strength')}
    },
    'toulvaddie': {
        'characteristics': '北ハイランド、テイン近郊。Heather Nelson女史創業のスコットランド初の女性単独経営蒸留所(計画中、2024年時点で建設中)。',
        'signature': {'name': 'Toulvaddie Single Malt (建設中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': NB('Pre-launch Founders Casks')}
    },
    'badachro': {
        'characteristics': '西ハイランド、ロス=シャー、ガイラックロッホ。2014年創業。ジン主体でシングルモルトも少量生産。',
        'signature': {'name': 'Badachro Gin', 'cask': '—', 'color': '—', 'taste': '海風、ボタニカル、地元由来'},
        'bottles': {'core': NB('Badachro Gin', 'Badachro Hebridean Pink Gin'), 'limited': NB('Badachro Single Malt (希少)')}
    },
    'balmaud': {
        'characteristics': '東ハイランド、アバディーンシャー。建設計画中の蒸留所、稼働開始未定。',
        'signature': {'name': 'Balmaud Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'dunnet_bay': {
        'characteristics': '北ハイランド、ケイスネス、ダネット。2014年創業のCaithnessのファミリービジネス。ジン"Rock Rose"、ウォッカ"Holy Grass"が看板で、シングルモルトは2024年〜熟成中。',
        'signature': {'name': 'Rock Rose Gin', 'cask': '—', 'color': '—', 'taste': 'ボタニカル、ローズヒップ、シーバックソーン'},
        'bottles': {'core': NB('Rock Rose Original Gin', 'Rock Rose Pink Grapefruit Gin', 'Holy Grass Vodka'), 'limited': NB('Dunnet Bay Single Malt (今後リリース予定)')}
    },
    'dunrobin': {
        'characteristics': '北ハイランド、サザーランド、ゴルスピー、ダンロビン城領内。建設計画中、稼働未定。',
        'signature': {'name': 'Dunrobin Castle Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'glen_luss': {
        'characteristics': '南ハイランド、ロッホ・ロモンド近郊、ルス。建設計画中、稼働未定。',
        'signature': {'name': 'Glen Luss Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'glen_quaich': {
        'characteristics': '南ハイランド、パースシャー、アムルリー。建設計画中、稼働未定。',
        'signature': {'name': 'Glen Quaich Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'keoldale': {
        'characteristics': '北西ハイランド、サザーランド、ダーネス。建設計画中、稼働未定。',
        'signature': {'name': 'Keoldale Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'lost_loch': {
        'characteristics': '東ハイランド、アバディーンシャー、アボイン。2019年創業のクラフト蒸留所。"Eight Lands"ブランドのオーガニック・ジン/ウォッカが看板。シングルモルトも生産。',
        'signature': {'name': 'Eight Lands Organic Vodka', 'cask': '—', 'color': '—', 'taste': '滑らか、ややフルーティ'},
        'bottles': {'core': NB('Eight Lands Organic Gin', 'Eight Lands Organic Vodka'), 'limited': NB('Lost Loch Single Malt (熟成中)')}
    },
    'midfearn': {
        'characteristics': '北ハイランド、Ardross Estate内。Ardross姉妹蒸留所として計画中、稼働未定。',
        'signature': {'name': 'Midfearn Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'portavadie': {
        'characteristics': '西ハイランド、アーガイル、ポータヴァディー。建設計画中、稼働未定。',
        'signature': {'name': 'Portavadie Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'speyside_no2': {
        'characteristics': 'ハイランド/スペイサイド境界、キンガッシー。Speyside Distillersの2号蒸留所として計画中。',
        'signature': {'name': 'Speyside No.2 Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'cairn': {
        'characteristics': 'スペイサイド、グランタウン・オン・スペイ。2022年Gordon & MacPhail創業。3代目Urquhart家族のヴィジョン。年産200万L、スチル2対。',
        'signature': {'name': 'The Cairn (NAS)', 'cask': 'バーボン樽+シェリー樽', 'color': 'ペールゴールド', 'taste': '蜂蜜、青リンゴ、シリアル、軽快、若々しい'},
        'bottles': {'core': NB('The Cairn (NAS)', 'The Cairn Bourbon Cask', 'The Cairn Sherry Cask'), 'limited': NB('Founders Edition', 'Cask Strength')}
    },
    'kinrara': {
        'characteristics': 'ハイランド、アヴィモア近郊。Kinrara Distillery計画中、未稼働。',
        'signature': {'name': 'Kinrara Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    # === Islands ===
    'abhainn_dearg': {
        'characteristics': '外ヘブリディーズ諸島ルイス島ウィグ。2008年Mark Tayburn氏創業、ルイス島初の合法蒸留所。スチル1対、年産2万L(超小規模)。ゲール語で"赤い川"の意。地元産大麦100%使用。',
        'signature': {'name': 'Abhainn Dearg Single Malt', 'cask': 'バーボン樽', 'color': 'ペールゴールド', 'taste': 'シリアル、ハニー、軽い海風、フローラル、純粋でスムース'},
        'bottles': {'core': NB('Abhainn Dearg Single Malt', 'Abhainn Dearg Spirit of Lewis (NAS)'), 'limited': NB('Abhainn Dearg Special Single Cask', 'Abhainn Dearg Extreme Old')}
    },
    'gramsdale': {
        'characteristics': '外ヘブリディーズ諸島ベンベキュラ島グラムズデール。Uist Distilling Co.が計画中。',
        'signature': {'name': 'Gramsdale Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'isle_of_barra': {
        'characteristics': '外ヘブリディーズ諸島バラ島キャッスルベイ。Isle of Barra Distillers計画中、ジンは先行販売。',
        'signature': {'name': 'Isle of Barra Atlantic Gin', 'cask': '—', 'color': '—', 'taste': 'カルガラスシードのボタニカル、塩気'},
        'bottles': {'core': NB('Isle of Barra Atlantic Gin'), 'limited': NB('Single Malt (将来計画)')}
    },
    'nunton': {
        'characteristics': '外ヘブリディーズ諸島ベンベキュラ島ナントン。Uist Distilling Co.の主蒸留所として計画中。',
        'signature': {'name': 'Nunton Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    # === Islay - Planned/New ===
    'laggan_bay': {
        'characteristics': 'アイラ島南部、ラガン湾。Elixir Distillers計画中、稼働開始予定2026年。',
        'signature': {'name': 'Laggan Bay Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'portintruan': {
        'characteristics': 'アイラ島南部、ポートエレン近郊。Elixir Distillers計画中、稼働未定。',
        'signature': {'name': 'Portintruan Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    # === Lowland - Active ===
    'eden_mill': {
        'characteristics': 'ローランド、ファイフ、セント・アンドルーズ。2014年創業、St Andrews Brewing Co系列。シングルモルト/ジン/ビールを統合した珍しい施設。スチル1対、年産10万L。2024年に新蒸留所建設中。',
        'signature': {'name': 'Eden Mill Hip Flask', 'cask': 'バーボン樽+シェリー樽', 'color': 'ゴールド', 'taste': 'シトラス、ハニー、軽いスパイス、フレッシュなローランド'},
        'bottles': {'core': NB('Eden Mill Hip Flask (NAS)', 'Eden Mill Reekie 25 (peated)', 'Eden Mill Original Gin'), 'limited': NB('Eden Mill Cask Strength', 'Single Cask Releases')}
    },
    'jackton': {
        'characteristics': 'ローランド、イースト・キルブライド近郊。2023年新設の蒸留所。',
        'signature': {'name': 'Jackton Single Malt (熟成中)', 'cask': 'バーボン樽+シェリー樽', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': NB('Jackton Inaugural Release (予定)')}
    },
    'leven': {
        'characteristics': 'ローランド、ファイフ、リーヴェン。Diageo計画中。',
        'signature': {'name': 'Leven Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'moffat': {
        'characteristics': 'ローランド、ダンフリースシャー、モファット。2022年Dark Sky Spirits創業のクラフト蒸留所。',
        'signature': {'name': 'Moffat Single Malt (熟成中)', 'cask': 'バーボン樽+シェリー樽', 'color': '—', 'taste': '—'},
        'bottles': {'core': NB('Dark Sky Vodka', 'Dark Sky Gin'), 'limited': NB('Moffat Distillery New Make')}
    },
    'borders_new': {
        'characteristics': 'ローランド、スコティッシュボーダーズ、ホーウィック。Three Stills Companyが計画中(既存Borders蒸留所と区別)。',
        'signature': {'name': 'Borders New Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'burnbrae': {
        'characteristics': 'ローランド、グラスゴー周辺。建設計画中。',
        'signature': {'name': 'Burnbrae Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'clutha': {
        'characteristics': 'ローランド、グラスゴー、クライド川沿い。建設計画中。',
        'signature': {'name': 'Clutha Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'crafty': {
        'characteristics': 'ローランド、ウィグタウンシャー、ニュートン・スチュワート。2019年Crafty Distillery創業。Hills & Harbour Ginが看板、シングルモルトも生産。',
        'signature': {'name': 'Crafty Single Malt', 'cask': 'バーボン樽', 'color': '—', 'taste': '若々しいモルト、シリアル、ハニー'},
        'bottles': {'core': NB('Hills & Harbour Gin', 'Crafty Single Malt (limited)'), 'limited': NB('Single Cask Releases')}
    },
    'midhope_castle': {
        'characteristics': 'ローランド、ウェスト・ロージアン、アバコーン、ミッドホープ城。建設計画中。',
        'signature': {'name': 'Midhope Castle Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'mossburn': {
        'characteristics': 'ローランド、スコティッシュボーダーズ、ジェドバラ近郊。2018年創業、Mossburn Distillers所有(Torabhaigと姉妹)。年産200万L。',
        'signature': {'name': 'Mossburn Single Malt (熟成中)', 'cask': 'バーボン樽+リフィル+シェリー', 'color': '—', 'taste': '—'},
        'bottles': {'core': NB('Mossburn Vintage Casks Speyside Bottlings', 'Mossburn Cask Bill No.1'), 'limited': NB('Mossburn Limited Edition Single Cask')}
    },
    'reivers': {
        'characteristics': 'ローランド、スコティッシュボーダーズ、ホーウィック。建設計画中。',
        'signature': {'name': 'Reivers Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'stirling': {
        'characteristics': 'ローランド、スターリング。2019年Stirling Distillery創業。シングルモルト+ジン製造。',
        'signature': {'name': 'Stirling Single Malt (熟成中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': NB('Stirling Gin', 'Stirling Spiced Rum'), 'limited': NB('Stirling Single Malt Inaugural Cask')}
    },
    'wolfcraig': {
        'characteristics': 'ローランド、スターリング近郊。Wolfcraig Distillers計画中。',
        'signature': {'name': 'Wolfcraig Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'chain_pier': {
        'characteristics': 'ローランド、エジンバラ近郊。Chain Pier Distillery計画中。',
        'signature': {'name': 'Chain Pier Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    # === Campbeltown ===
    'beinn_an_tuirc': {
        'characteristics': 'キャンベルタウン地区、カラデール、Torrisdale Castle Estate内。2019年創業。Kintyre Gin看板、シングルモルトは2024年〜。',
        'signature': {'name': 'Kintyre Single Malt (熟成中)', 'cask': 'バーボン樽+シェリー樽', 'color': '—', 'taste': '—'},
        'bottles': {'core': NB('Kintyre Gin', 'Kintyre Tarbert Legbiter Rum'), 'limited': NB('Beinn an Tuirc New Make', 'Kintyre Single Malt Inaugural')}
    },
    'dal_riata': {
        'characteristics': 'キャンベルタウン。Dal Riata Distillery計画中。',
        'signature': {'name': 'Dal Riata Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
    'machrihanish': {
        'characteristics': 'キャンベルタウン地区、マクリハニッシュ。建設計画中。',
        'signature': {'name': 'Machrihanish Single Malt (計画中)', 'cask': '—', 'color': '—', 'taste': '—'},
        'bottles': {'core': [], 'limited': []}
    },
}


def main():
    with open(DETAILS_FILE, encoding='utf-8') as f:
        details = json.load(f)
    added = 0
    for did, entry in ENTRIES.items():
        if did in details:
            continue
        entry['image'] = ''
        details[did] = entry
        added += 1
        print(f'Added: {did}')

    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print(f'\nTotal added: {added}')

    # Stats
    dist = json.load(open(ROOT / 'data' / 'distilleries.json', encoding='utf-8'))
    detail_ids = set(k for k in details if not k.startswith('_'))
    master_ids = set(x['id'] for x in dist['distilleries'])
    missing = master_ids - detail_ids
    print(f'Still missing: {len(missing)} / {len(master_ids)}')
    for m in sorted(missing):
        print(f'  {m}')


if __name__ == '__main__':
    main()
