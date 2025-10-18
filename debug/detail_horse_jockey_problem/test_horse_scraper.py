"""
馬情報のスクレイピングテスト
実際のURLを叩いて、馬の通算成績と親馬情報を取得する
"""

import requests
from bs4 import BeautifulSoup
import time
import json


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


def test_horse_overall_stats(horse_id: str):
    """
    馬の通算成績を取得
    """
    url = f"https://db.netkeiba.com/horse/{horse_id}"
    print(f"\n=== 馬情報取得テスト: {horse_id} ===")
    print(f"URL: {url}")

    soup = fetch_html(url)
    if not soup:
        return None

    # 馬名を取得
    horse_name_elem = soup.select_one('.horse_title h1')
    if horse_name_elem:
        print(f"\n馬名: {horse_name_elem.get_text(strip=True)}")

    # 通算成績を探す
    print("\n--- 通算成績を探す ---")

    # プロフィールテーブルを探す
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

                # 通算成績を探す
                if '成績' in header or '戦績' in header or '通算' in header:
                    print(f"  ★ 通算成績候補: {header} = {value}")

    # 馬の基本データテーブル
    print("\n--- 他のテーブルを探す ---")
    all_tables = soup.select('table')
    print(f"総テーブル数: {len(all_tables)}")

    for i, table in enumerate(all_tables):
        # テーブルのクラス名を確認
        classes = table.get('class', [])
        print(f"\nテーブル {i+1}: class={classes}")

        # 最初の数行を出力
        rows = table.select('tr')[:3]
        for row in rows:
            text = row.get_text(strip=True)
            if '成績' in text or '戦績' in text:
                print(f"  関連行: {text[:100]}")

    return soup


def test_parent_horses(horse_id: str):
    """
    親馬情報を取得
    """
    url = f"https://db.netkeiba.com/horse/{horse_id}"
    print(f"\n=== 親馬情報取得テスト: {horse_id} ===")

    soup = fetch_html(url)
    if not soup:
        return None

    # 血統テーブルを探す
    print("\n--- 血統テーブルを探す ---")

    blood_table = soup.select_one('.blood_table')
    if blood_table:
        print("\n血統テーブル発見:")
        rows = blood_table.select('tr')

        for i, row in enumerate(rows[:10]):
            cells = row.select('td')
            print(f"\n行 {i+1}:")
            for j, cell in enumerate(cells):
                link = cell.select_one('a')
                if link:
                    text = link.get_text(strip=True)
                    href = link.get('href', '')
                    print(f"  セル {j+1}: {text} (href: {href})")
                else:
                    text = cell.get_text(strip=True)
                    if text:
                        print(f"  セル {j+1}: {text}")
    else:
        print("血統テーブルが見つかりません")

        # 他のblood関連の要素を探す
        blood_elements = soup.select('[class*="blood"]')
        print(f"\nblood関連要素数: {len(blood_elements)}")
        for elem in blood_elements[:5]:
            print(f"  {elem.name}: {elem.get('class')}")

    # 血統図を探す
    pedigree_section = soup.select_one('#pedigree')
    if pedigree_section:
        print("\n血統図セクション発見")
        links = pedigree_section.select('a')
        for link in links[:10]:
            text = link.get_text(strip=True)
            href = link.get('href', '')
            if '/horse/' in href:
                print(f"  馬リンク: {text} (href: {href})")

    return soup


def main():
    """メインテスト実行"""

    # テスト対象の馬ID
    test_horse_id = "2023100452"

    print("=" * 60)
    print("馬情報スクレイピングテスト")
    print("=" * 60)

    # 通算成績のテスト
    horse_soup = test_horse_overall_stats(test_horse_id)

    time.sleep(2)  # サーバー負荷を考慮

    # 親馬情報のテスト
    parent_soup = test_parent_horses(test_horse_id)

    # HTMLを保存して後で確認できるようにする
    if horse_soup:
        with open('/Users/kai/programing/keiba_kaisetsu/debug/detail_horse_jockey_problem/horse_page.html', 'w', encoding='utf-8') as f:
            f.write(str(horse_soup.prettify()))
        print("\n\nHTMLを horse_page.html に保存しました")


if __name__ == "__main__":
    main()
