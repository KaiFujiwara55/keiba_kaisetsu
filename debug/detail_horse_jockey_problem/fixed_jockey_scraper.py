"""
修正版 ジョッキー情報スクレイパー
直近5年成績（累計勝率、連対率、複勝率）を正しく取得する
"""

import requests
from bs4 import BeautifulSoup
import re


class FixedJockeyScraper:
    """修正版 ジョッキー情報スクレイパー"""

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

    def fetch_jockey_stats(self, jockey_id: str):
        """
        ジョッキーの成績を取得

        Args:
            jockey_id: ジョッキーID

        Returns:
            Dict containing:
            - jockey_id: str
            - jockey_name: str
            - overall_stats: Dict (累計成績)
                - win_rate: float (勝率)
                - place_rate: float (連対率)
                - show_rate: float (複勝率)
                - wins: int (1着数)
                - seconds: int (2着数)
                - thirds: int (3着数)
                - total_races: int (総騎乗回数)
            - recent_5year_stats: Dict (直近5年成績)
                - win_rate: float (勝率)
                - place_rate: float (連対率)
                - show_rate: float (複勝率)
                - wins: int (1着数)
                - seconds: int (2着数)
                - thirds: int (3着数)
                - total_races: int (総騎乗回数)
        """
        url = f"{self.BASE_URL}/jockey/{jockey_id}"
        soup = self.fetch(url)
        if not soup:
            return None

        # ジョッキー名を取得
        jockey_name_elem = soup.select_one('.db_head_name h1')
        jockey_name = ""
        if jockey_name_elem:
            # 名前に改行や余分な空白が含まれる場合があるので整形
            jockey_name = re.sub(r'\s+', ' ', jockey_name_elem.get_text(strip=True))

        # 年度別成績テーブルから累計行と直近5年を取得
        # ResultsByYearsクラスを持つテーブルを探す
        results_tables = soup.select('table.ResultsByYears')

        overall_stats = {
            'win_rate': 0.0,
            'place_rate': 0.0,
            'show_rate': 0.0,
            'wins': 0,
            'seconds': 0,
            'thirds': 0,
            'total_races': 0
        }

        recent_5year_stats = {
            'win_rate': 0.0,
            'place_rate': 0.0,
            'show_rate': 0.0,
            'wins': 0,
            'seconds': 0,
            'thirds': 0,
            'total_races': 0
        }

        # 最初のテーブル（中央競馬）を使用
        if results_tables and len(results_tables) > 0:
            table = results_tables[0]
            tbody = table.select_one('tbody')

            if tbody:
                rows = tbody.select('tr')

                # 累計行を探す（最初の行が累計）
                if len(rows) > 0:
                    cumulative_row = rows[0]
                    first_cell = cumulative_row.select_one('td')
                    if first_cell and '累計' in first_cell.get_text(strip=True):
                        overall_stats = self._parse_stats_row(cumulative_row)

                # 直近5年のデータを集計（累計行を除く最初の5行）
                year_rows = [row for row in rows[1:6] if self._is_year_row(row)]
                if year_rows:
                    recent_5year_stats = self._aggregate_year_stats(year_rows)

        return {
            'jockey_id': jockey_id,
            'jockey_name': jockey_name,
            'overall_stats': overall_stats,
            'recent_5year_stats': recent_5year_stats
        }

    def _is_year_row(self, row):
        """行が年度データかどうかを判定"""
        first_cell = row.select_one('td')
        if not first_cell:
            return False

        text = first_cell.get_text(strip=True)
        # 4桁の年度（2020-2030など）かどうか
        return bool(re.match(r'^20\d{2}$', text))

    def _parse_stats_row(self, row):
        """
        成績行をパース

        テーブルの列構成:
        年度 | 順位 | 1着 | 2着 | 3着 | 4着〜 | 騎乗回数 | 重賞出走 | 重賞勝利 | 勝率 | 連対率 | 複勝率 | 代表馬
        0      1      2     3     4     5        6         7        8        9     10      11      12
        """
        cells = row.select('td')

        stats = {
            'wins': 0,
            'seconds': 0,
            'thirds': 0,
            'total_races': 0,
            'win_rate': 0.0,
            'place_rate': 0.0,
            'show_rate': 0.0
        }

        if len(cells) < 12:
            return stats

        # 1着（インデックス2）
        stats['wins'] = self._parse_int(cells[2].get_text(strip=True))

        # 2着（インデックス3）
        stats['seconds'] = self._parse_int(cells[3].get_text(strip=True))

        # 3着（インデックス4）
        stats['thirds'] = self._parse_int(cells[4].get_text(strip=True))

        # 騎乗回数（インデックス6）
        stats['total_races'] = self._parse_int(cells[6].get_text(strip=True))

        # 勝率（インデックス9）
        stats['win_rate'] = self._parse_percentage(cells[9].get_text(strip=True))

        # 連対率（インデックス10）
        stats['place_rate'] = self._parse_percentage(cells[10].get_text(strip=True))

        # 複勝率（インデックス11）
        stats['show_rate'] = self._parse_percentage(cells[11].get_text(strip=True))

        return stats

    def _aggregate_year_stats(self, year_rows):
        """
        複数年度の成績を集計

        Args:
            year_rows: 年度行のリスト

        Returns:
            集計された成績
        """
        total_wins = 0
        total_seconds = 0
        total_thirds = 0
        total_races = 0

        for row in year_rows:
            stats = self._parse_stats_row(row)
            total_wins += stats['wins']
            total_seconds += stats['seconds']
            total_thirds += stats['thirds']
            total_races += stats['total_races']

        # 勝率、連対率、複勝率を計算
        win_rate = 0.0
        place_rate = 0.0
        show_rate = 0.0

        if total_races > 0:
            win_rate = round((total_wins / total_races) * 100, 1)
            place_rate = round(((total_wins + total_seconds) / total_races) * 100, 1)
            show_rate = round(((total_wins + total_seconds + total_thirds) / total_races) * 100, 1)

        return {
            'wins': total_wins,
            'seconds': total_seconds,
            'thirds': total_thirds,
            'total_races': total_races,
            'win_rate': win_rate,
            'place_rate': place_rate,
            'show_rate': show_rate
        }

    def _parse_int(self, text: str) -> int:
        """
        整数をパース

        Args:
            text: テキスト

        Returns:
            整数値
        """
        if not text:
            return 0

        # カンマを削除
        clean_text = text.replace(',', '').strip()

        # 数字のみを抽出
        numeric_part = ''.join(filter(str.isdigit, clean_text))

        if numeric_part:
            return int(numeric_part)

        return 0

    def _parse_percentage(self, text: str) -> float:
        """
        パーセンテージをパース

        Args:
            text: テキスト（例: "7.7％" or "16.1％"）

        Returns:
            パーセンテージ値（float）
        """
        if not text:
            return 0.0

        # ％記号を削除
        clean_text = text.replace('%', '').replace('％', '').strip()

        try:
            return float(clean_text)
        except ValueError:
            return 0.0


def test_fixed_jockey_scraper():
    """修正版ジョッキースクレイパーのテスト"""

    scraper = FixedJockeyScraper()
    test_jockey_id = "01157"

    print("=" * 60)
    print("修正版 ジョッキー情報スクレイパー テスト")
    print("=" * 60)

    # ジョッキー成績のテスト
    print("\n--- ジョッキー成績取得テスト ---")
    jockey_stats = scraper.fetch_jockey_stats(test_jockey_id)

    if jockey_stats:
        print(f"\nジョッキーID: {jockey_stats['jockey_id']}")
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
        print("ジョッキー成績の取得に失敗しました")


if __name__ == "__main__":
    test_fixed_jockey_scraper()
