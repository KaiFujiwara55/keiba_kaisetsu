"""
修正後のスクレイパーのテストコード
"""

import sys
sys.path.append('/Users/kai/programing/keiba_kaisetsu')

from scraper.horse import HorseScraper
from scraper.jockey import JockeyScraper


def test_horse_scraper():
    """馬スクレイパーのテスト"""
    print("=" * 80)
    print("馬スクレイパーのテスト")
    print("=" * 80)

    scraper = HorseScraper()
    test_horse_id = "2023100452"

    # 通算成績のテスト
    print("\n--- 通算成績 ---")
    overall_stats = scraper.fetch_overall_stats(test_horse_id)
    if overall_stats:
        print(f"馬ID: {overall_stats['horse_id']}")
        print(f"馬名: {overall_stats['horse_name']}")
        print(f"通算成績: {overall_stats['overall_record']}")
        print(f"勝利数: {overall_stats['wins']}")
        print(f"総レース数: {overall_stats['races']}")
    else:
        print("通算成績の取得に失敗")

    # 親馬情報のテスト
    print("\n--- 親馬情報 ---")
    parent_info = scraper.fetch_parent_horses(test_horse_id)
    if parent_info:
        print(f"馬ID: {parent_info['horse_id']}")
        print(f"父馬: {parent_info['sire']['name']} (ID: {parent_info['sire']['id']})")
        print(f"母馬: {parent_info['dam']['name']} (ID: {parent_info['dam']['id']})")
    else:
        print("親馬情報の取得に失敗")

    # 競走成績のテスト（最初の5レース）
    print("\n--- 競走成績（最初の5レース） ---")
    race_results_horse_id = "2021104354"  # より多くのレース記録がある馬
    race_results = scraper.fetch_race_results(race_results_horse_id, limit=5)
    if race_results and race_results['results']:
        print(f"馬ID: {race_results['horse_id']}")
        print(f"総レース数: {len(race_results['results'])}\n")

        for i, race in enumerate(race_results['results']):
            print(f"レース {i+1}:")
            print(f"  日付: {race['date']}")
            print(f"  開催場所: {race['venue']}")
            print(f"  距離: {race['distance']} (馬場: {race['track_type']}, {race['distance_meters']}m)")
            print(f"  馬場状態: {race['track_condition']}")
            print(f"  タイム: {race['time']}")
            print(f"  着順: {race['finish_position']}着")
            print()
    else:
        print("競走成績の取得に失敗")


def test_jockey_scraper():
    """ジョッキースクレイパーのテスト"""
    print("\n" + "=" * 80)
    print("ジョッキースクレイパーのテスト")
    print("=" * 80)

    scraper = JockeyScraper()
    test_jockey_id = "01157"

    print("\n--- ジョッキー成績 ---")
    jockey_stats = scraper.fetch_jockey_stats(test_jockey_id)

    if jockey_stats:
        print(f"ジョッキーID: {jockey_stats['jockey_id']}")
        print(f"ジョッキー名: {jockey_stats['jockey_name']}")

        print("\n【累計成績】")
        overall = jockey_stats['overall_stats']
        print(f"  総騎乗回数: {overall['total_races']}")
        print(f"  1着: {overall['wins']}")
        print(f"  2着: {overall['seconds']}")
        print(f"  3着: {overall['thirds']}")
        print(f"  勝率: {overall['win_rate']}%")
        print(f"  連対率: {overall['place_rate']}%")
        print(f"  複勝率: {overall['show_rate']}%")

        print("\n【直近5年成績】")
        recent = jockey_stats['recent_5year_stats']
        print(f"  総騎乗回数: {recent['total_races']}")
        print(f"  1着: {recent['wins']}")
        print(f"  2着: {recent['seconds']}")
        print(f"  3着: {recent['thirds']}")
        print(f"  勝率: {recent['win_rate']}%")
        print(f"  連対率: {recent['place_rate']}%")
        print(f"  複勝率: {recent['show_rate']}%")
    else:
        print("ジョッキー成績の取得に失敗")


if __name__ == "__main__":
    test_horse_scraper()
    test_jockey_scraper()
