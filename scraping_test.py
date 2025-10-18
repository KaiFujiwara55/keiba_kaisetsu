#!/usr/bin/env python3
"""
netkeibaスクレイピング調査スクリプト
各URLにアクセスして、requestsだけで取得できるか検証
"""

import requests
from bs4 import BeautifulSoup
import json
import time

# User-Agent設定（ブラウザっぽく見せる）
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def test_race_list_page():
    """テスト1: レース一覧ページ（race_id取得）"""
    print("\n" + "="*80)
    print("テスト1: レース一覧ページ")
    print("="*80)

    url = "https://race.netkeiba.com/top/?kaisai_date=20251019"
    print(f"URL: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンスサイズ: {len(response.text)} bytes")

        # HTMLを保存
        with open('/Users/kai/programing/keiba_kaisetsu/USER/test1_race_list.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        # BeautifulSoupでパース
        soup = BeautifulSoup(response.text, 'html.parser')

        # race_idを含むリンクを探す
        race_links = soup.find_all('a', href=True)
        race_ids = []
        for link in race_links:
            href = link.get('href', '')
            if 'race_id=' in href:
                # race_idを抽出
                race_id = href.split('race_id=')[1].split('&')[0]
                race_ids.append(race_id)

        print(f"\n見つかったrace_id数: {len(set(race_ids))}")
        print(f"race_idサンプル（重複除去）: {list(set(race_ids))[:5]}")

        # JavaScriptタグの有無確認
        scripts = soup.find_all('script')
        print(f"\nJavaScriptタグ数: {len(scripts)}")

        return {
            "success": True,
            "status_code": response.status_code,
            "race_ids_found": len(set(race_ids)),
            "can_use_requests": len(race_ids) > 0
        }

    except Exception as e:
        print(f"エラー: {e}")
        return {"success": False, "error": str(e)}


def test_race_detail_page():
    """テスト2: レース詳細ページ（出走馬情報）"""
    print("\n" + "="*80)
    print("テスト2: レース詳細ページ")
    print("="*80)

    url = "https://race.netkeiba.com/race/shutuba.html?race_id=202505040701&rf=race_list"
    print(f"URL: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンスサイズ: {len(response.text)} bytes")

        # HTMLを保存
        with open('/Users/kai/programing/keiba_kaisetsu/USER/test2_race_detail.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')

        # 必要な情報を探す
        results = {
            "distance": None,
            "track_type": None,
            "horses": []
        }

        # 距離・馬場情報（よくあるパターン）
        race_data = soup.find('div', class_='RaceData01') or soup.find('span', class_='RaceData')
        if race_data:
            results["distance"] = race_data.get_text(strip=True)[:50]

        # 馬情報（テーブルから取得を試みる）
        horse_table = soup.find('table', class_='Shutuba_Table') or soup.find('table')
        if horse_table:
            rows = horse_table.find_all('tr')
            print(f"\nテーブル行数: {len(rows)}")

            for row in rows[:3]:  # 最初の3行だけ確認
                cells = row.find_all(['td', 'th'])
                if len(cells) > 0:
                    row_text = ' | '.join([cell.get_text(strip=True)[:20] for cell in cells[:6]])
                    print(f"行サンプル: {row_text}")

        # horse_idを含むリンクを探す
        horse_links = soup.find_all('a', href=True)
        horse_ids = []
        jockey_ids = []

        for link in horse_links:
            href = link.get('href', '')
            if '/horse/' in href:
                horse_id = href.split('/horse/')[-1].split('/')[0].split('?')[0]
                if horse_id.isdigit():
                    horse_ids.append(horse_id)
            if '/jockey/' in href:
                jockey_id = href.split('/jockey/')[-1].split('/')[0].split('?')[0]
                if jockey_id:
                    jockey_ids.append(jockey_id)

        print(f"\n見つかったhorse_id数: {len(horse_ids)}")
        print(f"horse_idサンプル: {horse_ids[:3]}")
        print(f"見つかったjockey_id数: {len(jockey_ids)}")
        print(f"jockey_idサンプル: {jockey_ids[:3]}")

        return {
            "success": True,
            "status_code": response.status_code,
            "horse_ids_found": len(horse_ids),
            "jockey_ids_found": len(jockey_ids),
            "can_use_requests": len(horse_ids) > 0
        }

    except Exception as e:
        print(f"エラー: {e}")
        return {"success": False, "error": str(e)}


def test_horse_page():
    """テスト3: 馬詳細ページ"""
    print("\n" + "="*80)
    print("テスト3: 馬詳細ページ")
    print("="*80)

    url = "https://db.netkeiba.com/horse/2023102602"
    print(f"URL: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンスサイズ: {len(response.text)} bytes")

        # HTMLを保存
        with open('/Users/kai/programing/keiba_kaisetsu/USER/test3_horse.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')

        # 戦績テーブルを探す
        tables = soup.find_all('table')
        print(f"\nテーブル数: {len(tables)}")

        for i, table in enumerate(tables[:2]):  # 最初の2つだけ確認
            print(f"\n--- テーブル {i+1} ---")
            rows = table.find_all('tr')[:3]  # 最初の3行
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) > 0:
                    row_text = ' | '.join([cell.get_text(strip=True)[:15] for cell in cells[:8]])
                    print(f"  {row_text}")

        return {
            "success": True,
            "status_code": response.status_code,
            "tables_found": len(tables),
            "can_use_requests": len(tables) > 0
        }

    except Exception as e:
        print(f"エラー: {e}")
        return {"success": False, "error": str(e)}


def test_jockey_page():
    """テスト4: 騎手詳細ページ"""
    print("\n" + "="*80)
    print("テスト4: 騎手詳細ページ")
    print("="*80)

    url = "https://db.netkeiba.com/jockey/01214"
    print(f"URL: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンスサイズ: {len(response.text)} bytes")

        # HTMLを保存
        with open('/Users/kai/programing/keiba_kaisetsu/USER/test4_jockey.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')

        # 成績テーブルを探す
        tables = soup.find_all('table')
        print(f"\nテーブル数: {len(tables)}")

        for i, table in enumerate(tables[:2]):
            print(f"\n--- テーブル {i+1} ---")
            rows = table.find_all('tr')[:3]
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) > 0:
                    row_text = ' | '.join([cell.get_text(strip=True)[:15] for cell in cells[:8]])
                    print(f"  {row_text}")

        return {
            "success": True,
            "status_code": response.status_code,
            "tables_found": len(tables),
            "can_use_requests": len(tables) > 0
        }

    except Exception as e:
        print(f"エラー: {e}")
        return {"success": False, "error": str(e)}


def main():
    print("netkeibaスクレイピング調査開始")
    print("="*80)

    results = {}

    # テスト実行
    time.sleep(1)  # サーバーに優しく
    results['test1'] = test_race_list_page()

    time.sleep(1)
    results['test2'] = test_race_detail_page()

    time.sleep(1)
    results['test3'] = test_horse_page()

    time.sleep(1)
    results['test4'] = test_jockey_page()

    # 結果サマリー
    print("\n" + "="*80)
    print("結果サマリー")
    print("="*80)

    summary = {
        "test1_race_list": results['test1'].get('can_use_requests', False),
        "test2_race_detail": results['test2'].get('can_use_requests', False),
        "test3_horse": results['test3'].get('can_use_requests', False),
        "test4_jockey": results['test4'].get('can_use_requests', False),
    }

    for test_name, can_use_requests in summary.items():
        status = "✓ requestsで取得可能" if can_use_requests else "✗ Selenium必要かも"
        print(f"{test_name}: {status}")

    all_ok = all(summary.values())
    print(f"\n総合判定: {'requestsのみで実装可能' if all_ok else 'Seleniumの使用を検討すべき'}")

    # 結果をJSONで保存
    with open('/Users/kai/programing/keiba_kaisetsu/USER/scraping_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n詳細結果: USER/scraping_test_results.json")
    print("HTMLファイル: USER/test*.html")


if __name__ == "__main__":
    main()
