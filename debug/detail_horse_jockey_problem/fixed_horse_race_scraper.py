"""
修正版 馬の競走成績スクレイパー
競走成績の全データを取得する
"""

import requests
from bs4 import BeautifulSoup
import re


class FixedHorseRaceScraper:
    """修正版 馬の競走成績スクレイパー"""

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

    def fetch_race_results(self, horse_id: str, limit: int = None):
        """
        馬の競走成績を全て取得

        Args:
            horse_id: 馬ID
            limit: 取得する最大レース数（Noneの場合は全て取得）

        Returns:
            Dict containing:
            - horse_id: str
            - results: List[Dict] - 競走成績のリスト
                各レースの情報:
                - date: str (日付)
                - venue: str (開催場所)
                - weather: str (天気)
                - race_number: str (R)
                - race_name: str (レース名)
                - num_horses: str (頭数)
                - gate_number: str (枠番)
                - horse_number: str (馬番)
                - odds: str (オッズ)
                - popularity: str (人気)
                - finish_position: str (着順)
                - jockey: str (騎手)
                - weight: str (斤量)
                - distance: str (距離、例: ダ1500)
                - track_condition: str (馬場状態、例: 良)
                - track_index: str (馬場指数)
                - time: str (タイム)
                - margin: str (着差)
                - time_index: str (タイム指数)
                - passing: str (通過)
                - pace: str (ペース)
                - last_3f: str (上り)
                - horse_weight: str (馬体重)
                - trainer_comment: str (厩舎コメント)
                - note: str (備考)
                - winner: str (勝ち馬)
                - prize: str (賞金)
        """
        url = f"{self.BASE_URL}/horse/result/{horse_id}"
        soup = self.fetch(url)
        if not soup:
            return None

        # 競走成績テーブルを取得
        race_results_table = soup.select_one('.db_h_race_results')
        if not race_results_table:
            return {
                'horse_id': horse_id,
                'results': []
            }

        results = []
        data_rows = race_results_table.select('tbody tr')

        # limitが指定されている場合は制限
        if limit:
            data_rows = data_rows[:limit]

        for row in data_rows:
            cells = row.select('td')

            if len(cells) < 20:  # 最低限必要な列数
                continue

            # 各セルからデータを取得
            race_data = {
                'date': self._get_cell_text(cells, 0),
                'venue': self._get_cell_text(cells, 1),
                'weather': self._get_cell_text(cells, 2),
                'race_number': self._get_cell_text(cells, 3),
                'race_name': self._get_cell_text(cells, 4),
                'num_horses': self._get_cell_text(cells, 6),
                'gate_number': self._get_cell_text(cells, 7),
                'horse_number': self._get_cell_text(cells, 8),
                'odds': self._get_cell_text(cells, 9),
                'popularity': self._get_cell_text(cells, 10),
                'finish_position': self._get_cell_text(cells, 11),
                'jockey': self._get_cell_text(cells, 12),
                'weight': self._get_cell_text(cells, 13),
                'distance': self._get_cell_text(cells, 14),
                'track_condition': self._get_cell_text(cells, 16),
                'track_index': self._get_cell_text(cells, 17),
                'time': self._get_cell_text(cells, 18),
                'margin': self._get_cell_text(cells, 19),
                'time_index': self._get_cell_text(cells, 20) if len(cells) > 20 else '',
                'passing': self._get_cell_text(cells, 21) if len(cells) > 21 else '',
                'pace': self._get_cell_text(cells, 22) if len(cells) > 22 else '',
                'last_3f': self._get_cell_text(cells, 23) if len(cells) > 23 else '',
                'horse_weight': self._get_cell_text(cells, 24) if len(cells) > 24 else '',
                'trainer_comment': self._get_cell_text(cells, 25) if len(cells) > 25 else '',
                'note': self._get_cell_text(cells, 26) if len(cells) > 26 else '',
                'winner': self._get_cell_text(cells, 27) if len(cells) > 27 else '',
                'prize': self._get_cell_text(cells, 28) if len(cells) > 28 else '',
            }

            # 距離から馬場タイプと距離を分離
            distance_info = self._parse_distance(race_data['distance'])
            race_data['track_type'] = distance_info['track_type']  # 芝/ダート
            race_data['distance_meters'] = distance_info['distance_meters']  # 距離（メートル）

            results.append(race_data)

        return {
            'horse_id': horse_id,
            'results': results
        }

    def _get_cell_text(self, cells, index):
        """セルからテキストを安全に取得"""
        if index < len(cells):
            return cells[index].get_text(strip=True)
        return ''

    def _parse_distance(self, distance_str: str):
        """
        距離文字列をパース

        Args:
            distance_str: 距離文字列（例: "ダ1500", "芝2000"）

        Returns:
            Dict with:
            - track_type: str (芝/ダート)
            - distance_meters: int (距離メートル)
        """
        track_type = ''
        distance_meters = 0

        if not distance_str:
            return {'track_type': track_type, 'distance_meters': distance_meters}

        # 芝/ダート/障を判定
        if '芝' in distance_str:
            track_type = '芝'
        elif 'ダ' in distance_str:
            track_type = 'ダート'
        elif '障' in distance_str:
            track_type = '障害'

        # 距離を抽出（数字部分）
        match = re.search(r'(\d+)', distance_str)
        if match:
            distance_meters = int(match.group(1))

        return {
            'track_type': track_type,
            'distance_meters': distance_meters
        }


def test_fixed_race_scraper():
    """修正版競走成績スクレイパーのテスト"""

    scraper = FixedHorseRaceScraper()
    test_horse_id = "2021104354"

    print("=" * 80)
    print("修正版 馬の競走成績スクレイパー テスト")
    print("=" * 80)

    # 競走成績のテスト（最初の10レースのみ）
    print("\n--- 競走成績取得テスト ---")
    race_results = scraper.fetch_race_results(test_horse_id, limit=10)

    if race_results and race_results['results']:
        print(f"\n馬ID: {race_results['horse_id']}")
        print(f"総レース数: {len(race_results['results'])}")

        # 最初の3レースを詳細表示
        for i, race in enumerate(race_results['results'][:3]):
            print(f"\n{'='*60}")
            print(f"レース {i+1}")
            print(f"{'='*60}")
            print(f"日付: {race['date']}")
            print(f"開催場所: {race['venue']}")
            print(f"天気: {race['weather']}")
            print(f"R: {race['race_number']}")
            print(f"レース名: {race['race_name']}")
            print(f"頭数: {race['num_horses']}")
            print(f"枠番: {race['gate_number']}")
            print(f"馬番: {race['horse_number']}")
            print(f"オッズ: {race['odds']}")
            print(f"人気: {race['popularity']}")
            print(f"着順: {race['finish_position']}")
            print(f"騎手: {race['jockey']}")
            print(f"斤量: {race['weight']}")
            print(f"距離: {race['distance']} (馬場: {race['track_type']}, 距離: {race['distance_meters']}m)")
            print(f"馬場状態: {race['track_condition']}")
            print(f"馬場指数: {race['track_index']}")
            print(f"タイム: {race['time']}")
            print(f"着差: {race['margin']}")
            print(f"タイム指数: {race['time_index']}")
            print(f"通過: {race['passing']}")
            print(f"ペース: {race['pace']}")
            print(f"上り: {race['last_3f']}")
            print(f"馬体重: {race['horse_weight']}")
            print(f"厩舎コメント: {race['trainer_comment']}")
            print(f"備考: {race['note']}")
            print(f"勝ち馬: {race['winner']}")
            print(f"賞金: {race['prize']}")

        # 全レースの簡易サマリー
        print(f"\n{'='*60}")
        print("全レースのサマリー")
        print(f"{'='*60}")
        for i, race in enumerate(race_results['results']):
            print(f"{i+1:2d}. {race['date']} {race['venue']:6s} {race['track_type']:4s}{race['distance_meters']:4d}m "
                  f"{race['track_condition']:2s} {race['finish_position']:3s}着 {race['time']:8s}")

    else:
        print("競走成績の取得に失敗しました")


if __name__ == "__main__":
    test_fixed_race_scraper()
