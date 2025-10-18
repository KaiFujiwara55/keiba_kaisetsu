"""
修正版 馬情報スクレイパー
通算成績と親馬情報を正しく取得する
"""

import requests
from bs4 import BeautifulSoup
import re


class FixedHorseScraper:
    """修正版 馬情報スクレイパー"""

    BASE_URL = "https://db.netkeiba.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch(self, url: str):
        """URLからHTMLを取得"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def fetch_overall_stats(self, horse_id: str):
        """
        馬の通算成績を取得

        Args:
            horse_id: 馬ID

        Returns:
            Dict containing:
            - horse_id: str
            - horse_name: str
            - overall_record: str (例: "2戦0勝 [0-0-0-2]")
            - wins: int (勝利数)
            - races: int (総レース数)
        """
        url = f"{self.BASE_URL}/horse/{horse_id}"
        soup = self.fetch(url)
        if not soup:
            return None

        # 馬名を取得
        horse_name_elem = soup.select_one('.horse_title h1')
        horse_name = horse_name_elem.get_text(strip=True) if horse_name_elem else ""

        # プロフィールテーブルから通算成績を取得
        profile_table = soup.select_one('.db_prof_table')
        overall_record = ""
        wins = 0
        races = 0

        if profile_table:
            rows = profile_table.select('tr')
            for row in rows:
                th = row.select_one('th')
                td = row.select_one('td')

                if th and td:
                    header = th.get_text(strip=True)
                    if '通算成績' in header:
                        overall_record = td.get_text(strip=True)

                        # "2戦0勝 [0-0-0-2]" のような形式から情報を抽出
                        # レース数を取得
                        races_match = re.search(r'(\d+)戦', overall_record)
                        if races_match:
                            races = int(races_match.group(1))

                        # 勝利数を取得
                        wins_match = re.search(r'(\d+)勝', overall_record)
                        if wins_match:
                            wins = int(wins_match.group(1))

                        break

        return {
            'horse_id': horse_id,
            'horse_name': horse_name,
            'overall_record': overall_record,
            'wins': wins,
            'races': races
        }

    def fetch_parent_horses(self, horse_id: str):
        """
        親馬情報を取得

        Args:
            horse_id: 馬ID

        Returns:
            Dict containing:
            - horse_id: str
            - sire: Dict (父馬情報)
                - name: str
                - id: str
            - dam: Dict (母馬情報)
                - name: str
                - id: str
        """
        # 血統ページにアクセス
        url = f"{self.BASE_URL}/horse/ped/{horse_id}"
        soup = self.fetch(url)
        if not soup:
            return None

        # 血統テーブルから父馬と母馬を取得
        blood_table = soup.select_one('.blood_table')
        sire_info = {'name': '', 'id': ''}
        dam_info = {'name': '', 'id': ''}

        if blood_table:
            rows = blood_table.select('tr')

            # 最初の行の最初のセルが父馬
            if len(rows) > 0:
                first_cell = rows[0].select_one('td a')
                if first_cell:
                    sire_info['name'] = first_cell.get_text(strip=True)
                    sire_href = first_cell.get('href', '')
                    sire_info['id'] = self._extract_horse_id_from_url(sire_href)

            # 母馬は通常9行目あたりにある（血統表の構造による）
            # より確実な方法: 2列目（左から2番目）の最初のセルを探す
            for i, row in enumerate(rows):
                cells = row.select('td')
                # 2番目の行（インデックス8-9あたり）で最初のセルを確認
                if i >= 8 and len(cells) > 0:
                    first_cell = cells[0].select_one('a')
                    if first_cell:
                        href = first_cell.get('href', '')
                        # 年代が19xx, 20xxの馬IDを持つものを母馬とみなす
                        horse_id_candidate = self._extract_horse_id_from_url(href)
                        if horse_id_candidate and (
                            horse_id_candidate.startswith('19') or
                            horse_id_candidate.startswith('20')
                        ):
                            dam_info['name'] = first_cell.get_text(strip=True)
                            dam_info['id'] = horse_id_candidate
                            break

        return {
            'horse_id': horse_id,
            'sire': sire_info,
            'dam': dam_info
        }

    def _extract_horse_id_from_url(self, url: str) -> str:
        """
        URLから馬IDを抽出

        Args:
            url: URL文字列

        Returns:
            馬ID or 空文字列
        """
        if not url or '/horse/' not in url:
            return ""

        # https://db.netkeiba.com/horse/2005102837/ のような形式
        match = re.search(r'/horse/([^/]+)', url)
        if match:
            return match.group(1)

        return ""


def test_fixed_scraper():
    """修正版スクレイパーのテスト"""

    scraper = FixedHorseScraper()
    test_horse_id = "2023100452"

    print("=" * 60)
    print("修正版 馬情報スクレイパー テスト")
    print("=" * 60)

    # 通算成績のテスト
    print("\n--- 通算成績取得テスト ---")
    overall_stats = scraper.fetch_overall_stats(test_horse_id)
    if overall_stats:
        print(f"馬ID: {overall_stats['horse_id']}")
        print(f"馬名: {overall_stats['horse_name']}")
        print(f"通算成績: {overall_stats['overall_record']}")
        print(f"勝利数: {overall_stats['wins']}")
        print(f"総レース数: {overall_stats['races']}")
    else:
        print("通算成績の取得に失敗しました")

    # 親馬情報のテスト
    print("\n--- 親馬情報取得テスト ---")
    parent_info = scraper.fetch_parent_horses(test_horse_id)
    if parent_info:
        print(f"馬ID: {parent_info['horse_id']}")
        print(f"父馬: {parent_info['sire']['name']} (ID: {parent_info['sire']['id']})")
        print(f"母馬: {parent_info['dam']['name']} (ID: {parent_info['dam']['id']})")
    else:
        print("親馬情報の取得に失敗しました")


if __name__ == "__main__":
    test_fixed_scraper()
