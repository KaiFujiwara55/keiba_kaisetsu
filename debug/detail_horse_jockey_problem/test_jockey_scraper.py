"""
ジョッキー情報のスクレイピングテスト
実際のURLを叩いて、ジョッキーの直近5年成績を取得する
"""

import requests
from bs4 import BeautifulSoup
import time


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


def test_jockey_stats(jockey_id: str):
    """
    ジョッキーの直近5年成績を取得
    - 累計勝率
    - 累計連帯率
    - 累計複勝率
    """
    url = f"https://db.netkeiba.com/jockey/{jockey_id}"
    print(f"\n=== ジョッキー情報取得テスト: {jockey_id} ===")
    print(f"URL: {url}")

    soup = fetch_html(url)
    if not soup:
        return None

    # ジョッキー名を取得
    jockey_name_elem = soup.select_one('.db_head_name h1')
    if jockey_name_elem:
        print(f"\nジョッキー名: {jockey_name_elem.get_text(strip=True)}")

    # プロフィールテーブルを探す
    print("\n--- プロフィールテーブルを探す ---")
    profile_table = soup.select_one('.db_prof_table')
    if profile_table:
        print("\nプロフィールテーブル発見:")
        rows = profile_table.select('tr')
        for row in rows:
            th = row.select_one('th')
            td = row.select_one('td')
            if th and td:
                header = th.get_text(strip=True)
                value = td.get_text(strip=True)
                print(f"  {header}: {value}")

                # 勝率・連帯率・複勝率を探す
                if '勝率' in header or '連帯率' in header or '複勝率' in header:
                    print(f"  ★ 成績指標発見: {header} = {value}")

    # 年度別成績テーブルを探す
    print("\n--- 年度別成績テーブルを探す ---")

    # よくある年度別成績のテーブル
    yearly_tables = [
        soup.select_one('.db_h_race_results'),
        soup.select_one('table.nk_tb_common'),
        soup.select_one('#contents_liquid table'),
    ]

    for i, table in enumerate(yearly_tables):
        if table:
            print(f"\n年度別テーブル候補 {i+1} 発見:")
            print(f"  クラス: {table.get('class', [])}")

            # ヘッダー行を確認
            header_row = table.select_one('thead tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.select('th')]
                print(f"  ヘッダー: {headers}")

            # データ行を確認
            data_rows = table.select('tbody tr')[:5]
            print(f"  データ行数: {len(data_rows)}")

            for j, row in enumerate(data_rows):
                cells = row.select('td')
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                print(f"    行 {j+1}: {cell_texts}")

    # 全テーブルを確認
    print("\n--- 全テーブルを確認 ---")
    all_tables = soup.select('table')
    print(f"総テーブル数: {len(all_tables)}")

    for i, table in enumerate(all_tables):
        classes = table.get('class', [])
        # 年度データがありそうなテーブルを探す
        first_row = table.select_one('tr')
        if first_row:
            text = first_row.get_text(strip=True)
            if '年度' in text or '勝' in text or '着' in text:
                print(f"\nテーブル {i+1}: class={classes}")
                print(f"  最初の行: {text[:100]}")

    return soup


def main():
    """メインテスト実行"""

    # テスト対象のジョッキーID
    test_jockey_id = "01157"

    print("=" * 60)
    print("ジョッキー情報スクレイピングテスト")
    print("=" * 60)

    # ジョッキー成績のテスト
    jockey_soup = test_jockey_stats(test_jockey_id)

    # HTMLを保存して後で確認できるようにする
    if jockey_soup:
        with open('/Users/kai/programing/keiba_kaisetsu/debug/detail_horse_jockey_problem/jockey_page.html', 'w', encoding='utf-8') as f:
            f.write(str(jockey_soup.prettify()))
        print("\n\nHTMLを jockey_page.html に保存しました")


if __name__ == "__main__":
    main()
