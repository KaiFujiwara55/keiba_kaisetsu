"""
馬の競走成績の詳細情報テスト
開催場所、距離、馬場、タイムを取得する
"""

import requests
from bs4 import BeautifulSoup


def fetch_html(url: str):
    """URLからHTMLを取得"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def test_horse_race_results(horse_id: str):
    """
    馬の競走成績を取得
    開催場所、距離、馬場、タイムを確認
    """
    url = f"https://db.netkeiba.com/horse/result/{horse_id}"
    print(f"\n=== 馬の競走成績詳細テスト: {horse_id} ===")
    print(f"URL: {url}")

    soup = fetch_html(url)
    if not soup:
        return None

    # 競走成績テーブルを探す
    print("\n--- 競走成績テーブルを探す ---")

    race_results_table = soup.select_one('.db_h_race_results')
    if race_results_table:
        print("\n競走成績テーブル発見:")

        # ヘッダーを確認
        header_row = race_results_table.select_one('thead tr')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.select('th')]
            print(f"\nヘッダー: {headers}")

        # データ行を確認（最初の5レース）
        data_rows = race_results_table.select('tbody tr')[:5]
        print(f"\nデータ行数: {len(data_rows)}")

        for i, row in enumerate(data_rows):
            print(f"\n--- レース {i+1} ---")
            cells = row.select('td')

            for j, cell in enumerate(cells[:20]):  # 最初の20列を確認
                text = cell.get_text(strip=True)
                print(f"  列 {j}: {text}")

    else:
        print("競走成績テーブルが見つかりません")

    return soup


def main():
    """メインテスト実行"""

    # テスト対象の馬ID（もっと競走成績が多い馬を使う）
    test_horse_id = "2021104354"  # より多くの競走実績がある馬

    print("=" * 60)
    print("馬の競走成績詳細テスト")
    print("=" * 60)

    # 競走成績のテスト
    horse_soup = test_horse_race_results(test_horse_id)

    # HTMLを保存して後で確認できるようにする
    if horse_soup:
        with open('/Users/kai/programing/keiba_kaisetsu/debug/detail_horse_jockey_problem/horse_race_results.html', 'w', encoding='utf-8') as f:
            f.write(str(horse_soup.prettify()))
        print("\n\nHTMLを horse_race_results.html に保存しました")


if __name__ == "__main__":
    main()
