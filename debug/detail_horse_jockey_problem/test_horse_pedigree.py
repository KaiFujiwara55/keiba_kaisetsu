"""
馬の血統情報のスクレイピングテスト
血統ページから親馬のIDを取得する
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


def test_horse_pedigree(horse_id: str):
    """
    馬の血統ページから親馬情報を取得
    """
    url = f"https://db.netkeiba.com/horse/ped/{horse_id}"
    print(f"\n=== 血統情報取得テスト: {horse_id} ===")
    print(f"URL: {url}")

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

    # Ajaxで読み込まれる可能性があるのでスクリプトタグも確認
    print("\n--- 他の方法で血統情報を探す ---")

    # すべてのhorse/のリンクを探す
    all_horse_links = soup.select('a[href*="/horse/"]')
    print(f"\n馬関連リンク数: {len(all_horse_links)}")

    for link in all_horse_links[:20]:
        text = link.get_text(strip=True)
        href = link.get('href', '')
        if text and '/ped/' not in href and '/result/' not in href:
            print(f"  {text}: {href}")

    return soup


def main():
    """メインテスト実行"""

    # テスト対象の馬ID
    test_horse_id = "2023100452"

    print("=" * 60)
    print("血統情報スクレイピングテスト")
    print("=" * 60)

    # 血統情報のテスト
    pedigree_soup = test_horse_pedigree(test_horse_id)

    # HTMLを保存して後で確認できるようにする
    if pedigree_soup:
        with open('/Users/kai/programing/keiba_kaisetsu/debug/detail_horse_jockey_problem/pedigree_page.html', 'w', encoding='utf-8') as f:
            f.write(str(pedigree_soup.prettify()))
        print("\n\nHTMLを pedigree_page.html に保存しました")


if __name__ == "__main__":
    main()
