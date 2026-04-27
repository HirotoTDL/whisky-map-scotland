#!/usr/bin/env python
"""52蒸留所の不足している詳細データを追加"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DETAILS_FILE = ROOT / 'data' / 'details.json'

# Major distilleries with widely-known official bottles
NEW_ENTRIES = {
    'longmorn': {
        'characteristics': 'スペイサイド、エルギン近郊のロングモーン村。1894年John Duff創業、Chivas Brothers (Pernod Ricard)所有。年産約450万L、スチル4対(ウォッシュ4+スピリット4)。仕込み水はマンノック丘陵泉。Chivas RegalブランドのキーモルトとしてDestillerが評価する伝説のスペイサイド。ノンチル濾過のリッチでバニラ・ハニー・トロピカルフルーツ系の酒質。',
        'signature': {
            'name': 'Longmorn 18 Year Old (Distillery Edition)',
            'cask': 'バーボン樽+シェリー樽',
            'color': 'ディープゴールド〜アンバー',
            'taste': 'リッチハニー、トロピカルフルーツ(マンゴー、パイナップル)、バニラ、シナモン、滑らかでクリーミーなテクスチャ、長い余韻'
        },
        'bottles': {
            'core': [
                {'name': 'Longmorn The Distiller\'s Choice (NAS)', 'type': '常売'},
                {'name': 'Longmorn 16 Year Old (旧コア、廃盤)', 'type': '希少'},
                {'name': 'Longmorn 18 Year Old', 'type': '常売'},
                {'name': 'Longmorn 23 Year Old', 'type': '常売'},
                {'name': 'Longmorn 25 Year Old', 'type': '常売(高熟成)'}
            ],
            'limited': [
                {'name': 'Longmorn 30 Year Old', 'type': '限定'},
                {'name': 'Longmorn Distillers Edition', 'type': '限定'},
                {'name': 'Vintage Releases (Gordon & MacPhail/Signatory)', 'type': '独立瓶詰'}
            ]
        }
    },
    'ben_nevis': {
        'characteristics': '西ハイランド、フォートウィリアム、ベン・ネヴィス山麓。1825年John MacDonald(Long John)創業、ニッカウヰスキー(アサヒグループ)所有(1989〜)。年産約200万L、スチル2対。仕込み水はアラン・ラ・モーリック泉。竹鶴政孝も学んだ蒸留所。リッチで複雑、シェリー樽熟成のアロマが特徴。',
        'signature': {
            'name': 'Ben Nevis 10 Year Old',
            'cask': 'バーボン樽主体+シェリー樽',
            'color': 'ディープアンバー',
            'taste': 'リッチモルト、ドライフルーツ、シェリー、ナッツ、軽いスモーク、フルボディで複雑'
        },
        'bottles': {
            'core': [
                {'name': 'Ben Nevis 10 Year Old', 'type': '常売'},
                {'name': 'Ben Nevis Coire Leis (NAS)', 'type': '常売'},
                {'name': 'McDonald\'s Traditional Ben Nevis (ピーテッド)', 'type': '常売'}
            ],
            'limited': [
                {'name': 'Ben Nevis 25 Year Old', 'type': '限定'},
                {'name': 'Ben Nevis 40 Year Old', 'type': '限定(超希少)'},
                {'name': 'Single Cask Releases', 'type': '限定'}
            ]
        }
    },
    'balblair': {
        'characteristics': '北ハイランド、ロス=シャー、エドダートン。1790年創業、スコットランド最古の現役蒸留所のひとつ。Inver House Distillers所有(1996〜)。年産約180万L、スチル2対。仕込み水はオールスメリル泉。映画"天使の分け前"の舞台としても知られる。バーボン樽主体の軽快でフルーティな酒質。',
        'signature': {
            'name': 'Balblair 12 Year Old',
            'cask': 'アメリカン・バーボン樽',
            'color': 'ペールゴールド',
            'taste': 'シトラス、青リンゴ、ヴァニラ、ハチミツ、オーク、ライトでフルーティ、エレガント'
        },
        'bottles': {
            'core': [
                {'name': 'Balblair 12 Year Old', 'type': '常売'},
                {'name': 'Balblair 15 Year Old', 'type': '常売'},
                {'name': 'Balblair 18 Year Old', 'type': '常売'},
                {'name': 'Balblair 25 Year Old', 'type': '常売'}
            ],
            'limited': [
                {'name': 'Balblair Vintage Releases (1989/1990/1999/2003等)', 'type': '限定'},
                {'name': 'Balblair 40 Year Old', 'type': '限定(超希少)'}
            ]
        }
    },
    'glengoyne': {
        'characteristics': '南ハイランドとローランドの境界(Highland Boundary Fault線上)、ダンゴイン。1833年創業、Ian Macleod Distillers所有(2003〜)。年産約110万L、スチル3基(ウォッシュ1+スピリット2)。仕込み水はダンゴイン丘陵泉。スコットランドで最も遅い蒸留速度("世界一スロー")で軽やかな酒質。ノンピート、シェリー樽中心。',
        'signature': {
            'name': 'Glengoyne 18 Year Old',
            'cask': 'ファーストフィル・シェリー樽+リフィル・バーボン樽',
            'color': 'ディープアンバー',
            'taste': 'シェリー、ドライフルーツ、ナッツ、シナモン、オレンジマーマレード、リッチで複雑、長く続く余韻'
        },
        'bottles': {
            'core': [
                {'name': 'Glengoyne 10 Year Old', 'type': '常売'},
                {'name': 'Glengoyne 12 Year Old', 'type': '常売'},
                {'name': 'Glengoyne 15 Year Old', 'type': '常売'},
                {'name': 'Glengoyne 18 Year Old', 'type': '常売'},
                {'name': 'Glengoyne 21 Year Old', 'type': '常売'},
                {'name': 'Glengoyne Cask Strength', 'type': '常売(バッチ毎)'}
            ],
            'limited': [
                {'name': 'Glengoyne 25 / 30 / 35 Year Old', 'type': '限定'},
                {'name': 'Teapot Dram (蒸留所限定)', 'type': '限定'},
                {'name': 'Legacy Series', 'type': '限定'}
            ]
        }
    },
    'glenturret': {
        'characteristics': '南ハイランド、パースシャー、クリーフ近郊。1775年創業、スコットランド現役最古の蒸留所(諸説あり)。Lalique Group所有(2019〜)。年産約34万L、スチル2基。仕込み水はターレット川。フェイマスグラウス・ブレンドの中核(以前)。2020年から新ブランドアイデンティティで単独瓶詰めにシフト。',
        'signature': {
            'name': 'Glenturret 12 Year Old (Maiden Release)',
            'cask': 'バーボン樽+シェリー樽',
            'color': 'ゴールド',
            'taste': 'ハニー、ドライフルーツ、スパイス、軽いスモーク、オーク、リッチで丸みのあるハイランドスタイル'
        },
        'bottles': {
            'core': [
                {'name': 'Glenturret Triple Wood (NAS)', 'type': '常売'},
                {'name': 'Glenturret 7 Year Old (Peat Smoked)', 'type': '常売'},
                {'name': 'Glenturret 10 Year Old', 'type': '常売'},
                {'name': 'Glenturret 12 Year Old', 'type': '常売'},
                {'name': 'Glenturret 15 Year Old', 'type': '常売'}
            ],
            'limited': [
                {'name': 'Glenturret 25 / 30 Year Old', 'type': '限定'},
                {'name': 'Lalique Series (Lalique decanter)', 'type': '限定(高級)'}
            ]
        }
    },
    'glencadam': {
        'characteristics': '東ハイランド、アンガス、ブレヒン。1825年創業、Angus Dundee Distillers所有(2003〜)。年産約130万L、スチル2基。仕込み水はLoch Lee。スチルのリン管が水平に近い独特設計で軽くフローラルな酒質。',
        'signature': {
            'name': 'Glencadam 15 Year Old',
            'cask': 'バーボン樽+シェリー樽',
            'color': 'ゴールド',
            'taste': 'フローラル、シトラス、青リンゴ、バニラ、ハニー、軽くてエレガント、Highland最軽量級'
        },
        'bottles': {
            'core': [
                {'name': 'Glencadam 10 Year Old', 'type': '常売'},
                {'name': 'Glencadam 13 Year Old (Re-awakening)', 'type': '常売'},
                {'name': 'Glencadam 15 Year Old', 'type': '常売'},
                {'name': 'Glencadam 17 Year Old (Triple Cask)', 'type': '常売'},
                {'name': 'Glencadam 18 Year Old', 'type': '常売'},
                {'name': 'Glencadam 21 Year Old', 'type': '常売'},
                {'name': 'Glencadam 25 Year Old', 'type': '常売'}
            ],
            'limited': [
                {'name': 'Glencadam Origin (1825)', 'type': '限定'},
                {'name': 'Vintage Releases', 'type': '限定'}
            ]
        }
    },
    'glenglassaugh': {
        'characteristics': '東ハイランド、ポートソイ、北海岸沿い。1875年創業、Brown-Forman所有(2016〜)。1986年閉鎖→2008年再開。年産約110万L、スチル2基。仕込み水はGlenglassaugh泉。海岸立地によるブリニーな(塩気のある)酒質。マスターブレンダーDr. Rachel Barrieが指揮。',
        'signature': {
            'name': 'Glenglassaugh Sandend',
            'cask': 'マンサニリャ・シェリー+バーボン樽',
            'color': 'ゴールド',
            'taste': '海風、ブリニー(塩気)、トロピカルフルーツ、バニラ、ハニー、軽くてリフレッシング'
        },
        'bottles': {
            'core': [
                {'name': 'Glenglassaugh Sandend (NAS)', 'type': '常売'},
                {'name': 'Glenglassaugh Portsoy (Peated NAS)', 'type': '常売'},
                {'name': 'Glenglassaugh 12 Year Old', 'type': '常売'}
            ],
            'limited': [
                {'name': 'Glenglassaugh 30 / 40 / 50 Year Old', 'type': '限定(高熟成)'},
                {'name': 'Octaves Series', 'type': '限定'},
                {'name': 'Coastal Cask Series', 'type': '限定'}
            ]
        }
    },
    'loch_lomond': {
        'characteristics': '南ハイランド、ロッホ・ロモンド南端、アレクサンドリア。1964年創業、Loch Lomond Group所有。スコットランドで最も多様な蒸留所のひとつ — モルト・グレーン両方を製造、独自のストレートネック・スチルで複数のスタイルを作り分け。年産約500万L(モルト)+1,800万L(グレーン)。シングルモルトは"Loch Lomond"と"Inchmurrin"、"Inchmoan"等複数銘柄。',
        'signature': {
            'name': 'Loch Lomond 12 Year Old',
            'cask': 'バーボン樽+リフィル+リチャード樽',
            'color': 'ゴールド',
            'taste': 'バナナ、ピーチ、ハニー、シリアル、軽いスモーク、フルーティでスムース'
        },
        'bottles': {
            'core': [
                {'name': 'Loch Lomond 12 Year Old', 'type': '常売'},
                {'name': 'Loch Lomond 14 Year Old', 'type': '常売'},
                {'name': 'Loch Lomond 18 Year Old', 'type': '常売'},
                {'name': 'Inchmurrin 12 / 18 Year Old', 'type': '常売'},
                {'name': 'Inchmoan 12 Year Old (Peated)', 'type': '常売'},
                {'name': 'Loch Lomond Original (NAS)', 'type': '常売'}
            ],
            'limited': [
                {'name': 'Loch Lomond 21 / 25 / 30 Year Old', 'type': '限定'},
                {'name': 'The Open Collaboration Series (golf)', 'type': '限定'},
                {'name': 'Single Cask Releases', 'type': '限定'}
            ]
        }
    },
    'tormore': {
        'characteristics': 'スペイサイド、アドヴィ。1958年創業(20世紀以降にスペイサイドで建造された数少ない蒸留所)、Elixir Distillers所有(2022〜)。装飾的な"Whisky Cathedral"建築で知られる。年産約470万L、スチル8基。',
        'signature': {
            'name': 'Tormore 14 Year Old',
            'cask': 'バーボン樽+シェリー樽',
            'color': 'ゴールド',
            'taste': '青リンゴ、洋梨、シトラス、バニラ、軽いスパイス、フルーティでスムースなスペイサイド'
        },
        'bottles': {
            'core': [
                {'name': 'Tormore 12 Year Old', 'type': '常売'},
                {'name': 'Tormore 14 Year Old', 'type': '常売'},
                {'name': 'Tormore 16 Year Old', 'type': '常売'}
            ],
            'limited': [
                {'name': 'Tormore Single Cask Series', 'type': '限定'},
                {'name': 'Vintage Releases (Gordon & MacPhail等)', 'type': '独立瓶詰'}
            ]
        }
    },
    'rosebank': {
        'characteristics': 'ローランド、フォルカーク、フォース・クライド運河沿い。1840年創業、1993年閉鎖→2023年Ian Macleod Distillersにより復活。"ローランドの女王"と称される伝統的な3回蒸留(triple distillation)の代表。年産約100万L、スチル3基。',
        'signature': {
            'name': 'Rosebank 30 Year Old (2020 Release)',
            'cask': 'バーボン樽+リフィル・シェリー樽',
            'color': 'ペールゴールド',
            'taste': '花、青リンゴ、シトラス、バニラ、ハニー、繊細でエレガント、3回蒸留らしい純度'
        },
        'bottles': {
            'core': [
                {'name': 'Rosebank Inaugural Release (2024〜、再開後新ボトル)', 'type': '常売予定'}
            ],
            'limited': [
                {'name': 'Rosebank 30 Year Old (2020/2021/2022 Release)', 'type': '限定'},
                {'name': 'Rosebank 31 / 32 / 33 Year Old', 'type': '限定'},
                {'name': 'Vintage Releases (G&M, Signatory等)', 'type': '独立瓶詰'}
            ]
        }
    }
}


def main():
    with open(DETAILS_FILE, encoding='utf-8') as f:
        details = json.load(f)
    added = 0
    for did, entry in NEW_ENTRIES.items():
        if did in details:
            continue
        # Add empty image fields to bottles (will be filled by scrapers)
        for section in ('core', 'limited'):
            for b in entry['bottles'].get(section, []):
                if 'image' not in b:
                    b['image'] = ''
        # No exterior image yet for these — UI will fall back to placeholder
        entry['image'] = ''
        details[did] = entry
        added += 1
        print(f'Added: {did}')

    with open(DETAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print(f'\nTotal added: {added}')


if __name__ == '__main__':
    main()
