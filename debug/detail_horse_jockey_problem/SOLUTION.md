# 馬・ジョッキー情報スクレイピング問題の解決策

## 問題概要

馬の情報とジョッキーの情報が正しくスクレイピングできていない問題について、実際のHTMLを調査して解決策を作成しました。

---

## 1. 馬情報の修正

### 1.1 通算成績の取得

**現状の問題:**
- 現在の実装では通算成績が正しく取得できていない

**解決策:**
- プロフィールテーブル（`.db_prof_table`）から「通算成績」行を探す
- データ形式: `"2戦0勝 [0-0-0-2]"`

**実装場所:**
- ファイル: `scraper/horse.py`
- メソッド: 新規追加 `fetch_overall_stats(horse_id)`

**実装例:**
```python
def fetch_overall_stats(self, horse_id: str):
    url = f"{self.BASE_URL}/horse/{horse_id}"
    soup = self.fetch(url)

    profile_table = soup.select_one('.db_prof_table')
    if profile_table:
        rows = profile_table.select('tr')
        for row in rows:
            th = row.select_one('th')
            td = row.select_one('td')
            if th and td and '通算成績' in th.get_text(strip=True):
                overall_record = td.get_text(strip=True)
                # "2戦0勝 [0-0-0-2]" から情報を抽出
                races_match = re.search(r'(\d+)戦', overall_record)
                wins_match = re.search(r'(\d+)勝', overall_record)
                return {
                    'overall_record': overall_record,
                    'wins': int(wins_match.group(1)) if wins_match else 0,
                    'races': int(races_match.group(1)) if races_match else 0
                }
```

---

### 1.2 親馬情報の取得

**現状の問題:**
- 血統情報が取得できていない（血統テーブルが見つからない）

**原因:**
- 血統情報は別ページ `/horse/ped/{horse_id}` にある

**解決策:**
- 血統ページ（`https://db.netkeiba.com/horse/ped/{horse_id}`）にアクセス
- `.blood_table` から父馬・母馬の情報を取得

**実装場所:**
- ファイル: `scraper/horse.py`
- メソッド: `fetch_parent_horses(horse_id)` を修正

**実装例:**
```python
def fetch_parent_horses(self, horse_id: str):
    # 血統ページにアクセス
    url = f"{self.BASE_URL}/horse/ped/{horse_id}"
    soup = self.fetch(url)

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

        # 母馬は行8-9あたりの最初のセル
        for i, row in enumerate(rows):
            if i >= 8:
                cells = row.select('td')
                if len(cells) > 0:
                    first_cell = cells[0].select_one('a')
                    if first_cell:
                        href = first_cell.get('href', '')
                        horse_id_candidate = self._extract_horse_id_from_url(href)
                        # 年代が19xx, 20xxの馬IDを母馬とみなす
                        if horse_id_candidate and (
                            horse_id_candidate.startswith('19') or
                            horse_id_candidate.startswith('20')
                        ):
                            dam_info['name'] = first_cell.get_text(strip=True)
                            dam_info['id'] = horse_id_candidate
                            break
```

---

### 1.3 競走成績の詳細取得（新規追加）

**要件:**
- 開催場所、距離、馬場、タイムを含む全競走成績を取得

**解決策:**
- 競走成績ページ（`https://db.netkeiba.com/horse/result/{horse_id}`）にアクセス
- `.db_h_race_results` テーブルから全データを取得

**実装場所:**
- ファイル: `scraper/horse.py`
- メソッド: 新規追加 `fetch_race_results(horse_id, limit=None)`

**取得データ:**
```python
race_data = {
    'date': str,              # 日付
    'venue': str,             # 開催場所（金沢、川崎など）
    'weather': str,           # 天気
    'race_number': str,       # R
    'race_name': str,         # レース名
    'num_horses': str,        # 頭数
    'gate_number': str,       # 枠番
    'horse_number': str,      # 馬番
    'odds': str,              # オッズ
    'popularity': str,        # 人気
    'finish_position': str,   # 着順
    'jockey': str,            # 騎手
    'weight': str,            # 斤量
    'distance': str,          # 距離（例: ダ1500）
    'track_type': str,        # 馬場タイプ（芝/ダート/障害）
    'distance_meters': int,   # 距離（メートル）
    'track_condition': str,   # 馬場状態（良/重/不良など）
    'track_index': str,       # 馬場指数
    'time': str,              # タイム（例: 1:42.5）
    'margin': str,            # 着差
    'time_index': str,        # タイム指数
    'passing': str,           # 通過
    'pace': str,              # ペース
    'last_3f': str,           # 上り（ラスト3ハロン）
    'horse_weight': str,      # 馬体重
    'trainer_comment': str,   # 厩舎コメント
    'note': str,              # 備考
    'winner': str,            # 勝ち馬
    'prize': str,             # 賞金
}
```

**列インデックス:**
```
0: 日付
1: 開催
2: 天気
3: R
4: レース名
6: 頭数
7: 枠番
8: 馬番
9: オッズ
10: 人気
11: 着順
12: 騎手
13: 斤量
14: 距離
16: 馬場状態
17: 馬場指数
18: タイム
19: 着差
20: タイム指数
21: 通過
22: ペース
23: 上り
24: 馬体重
25: 厩舎コメント
26: 備考
27: 勝ち馬
28: 賞金
```

---

## 2. ジョッキー情報の修正

### 2.1 直近5年成績の取得

**現状の問題:**
- 年度別成績テーブルが正しく取得できていない
- 勝率、連対率、複勝率が正しく計算できていない

**解決策:**
- `ResultsByYears` クラスを持つテーブルから累計行と年度行を取得
- 累計行（最初の行）から累計成績を取得
- 年度行（2行目以降の5行）から直近5年成績を集計

**実装場所:**
- ファイル: `scraper/jockey.py`
- メソッド: `fetch_jockey_stats(jockey_id)` を修正

**実装例:**
```python
def fetch_jockey_stats(self, jockey_id: str):
    url = f"{self.BASE_URL}/jockey/{jockey_id}"
    soup = self.fetch(url)

    # ResultsByYearsテーブルを取得
    results_tables = soup.select('table.ResultsByYears')

    if results_tables and len(results_tables) > 0:
        table = results_tables[0]  # 中央競馬のテーブル
        tbody = table.select_one('tbody')

        if tbody:
            rows = tbody.select('tr')

            # 累計行（最初の行）
            if len(rows) > 0:
                cumulative_row = rows[0]
                first_cell = cumulative_row.select_one('td')
                if first_cell and '累計' in first_cell.get_text(strip=True):
                    overall_stats = self._parse_stats_row(cumulative_row)

            # 直近5年の年度行を集計
            year_rows = [row for row in rows[1:6] if self._is_year_row(row)]
            if year_rows:
                recent_5year_stats = self._aggregate_year_stats(year_rows)
```

**統計行のパース:**
```python
def _parse_stats_row(self, row):
    """
    テーブルの列構成:
    0: 年度
    1: 順位
    2: 1着
    3: 2着
    4: 3着
    5: 4着〜
    6: 騎乗回数
    7: 重賞出走
    8: 重賞勝利
    9: 勝率
    10: 連対率
    11: 複勝率
    12: 代表馬
    """
    cells = row.select('td')

    return {
        'wins': self._parse_int(cells[2].get_text(strip=True)),
        'seconds': self._parse_int(cells[3].get_text(strip=True)),
        'thirds': self._parse_int(cells[4].get_text(strip=True)),
        'total_races': self._parse_int(cells[6].get_text(strip=True)),
        'win_rate': self._parse_percentage(cells[9].get_text(strip=True)),
        'place_rate': self._parse_percentage(cells[10].get_text(strip=True)),
        'show_rate': self._parse_percentage(cells[11].get_text(strip=True))
    }
```

---

## 3. 実装ファイル

修正版の実装は以下のファイルに作成しました:

### テストコード（debug/detail_horse_jockey_problem/）
1. `test_horse_scraper.py` - 馬情報のHTML調査
2. `test_jockey_scraper.py` - ジョッキー情報のHTML調査
3. `test_horse_pedigree.py` - 血統情報のHTML調査
4. `test_horse_race_details.py` - 競走成績のHTML調査

### 修正版スクレイパー（debug/detail_horse_jockey_problem/）
1. `fixed_horse_scraper.py` - 馬の通算成績・親馬情報
2. `fixed_jockey_scraper.py` - ジョッキーの累計・直近5年成績
3. `fixed_horse_race_scraper.py` - 馬の競走成績全データ

---

## 4. scraper配下への適用方法

### 4.1 scraper/horse.py の修正

#### 追加メソッド:
```python
def fetch_overall_stats(self, horse_id: str) -> Optional[Dict]:
    """通算成績を取得"""
    # fixed_horse_scraper.py の実装を参照

def fetch_race_results(self, horse_id: str, limit: int = None) -> Optional[Dict]:
    """競走成績を全て取得"""
    # fixed_horse_race_scraper.py の実装を参照
```

#### 修正メソッド:
```python
def fetch_parent_horses(self, horse_id: str) -> Optional[Dict]:
    """親馬情報を取得（血統ページから）"""
    # URLを /horse/ped/{horse_id} に変更
    # fixed_horse_scraper.py の実装を参照
```

### 4.2 scraper/jockey.py の修正

#### 修正メソッド:
```python
def fetch_jockey_stats(self, jockey_id: str) -> Optional[Dict]:
    """ジョッキー成績を取得（累計と直近5年）"""
    # ResultsByYearsテーブルから取得
    # fixed_jockey_scraper.py の実装を参照
```

---

## 5. テスト結果

### 5.1 馬情報（馬ID: 2023100452）

**通算成績:**
- 通算成績: "2戦0勝 [0-0-0-2]"
- 勝利数: 0
- 総レース数: 2

**親馬情報:**
- 父馬: エスポワールシチー (ID: 2005102837)
- 母馬: エミネントシチー (ID: 1998106179)

**競走成績（馬ID: 2021104354 で検証）:**
```
 1. 2024/09/30 金沢 ダート 1500m 良  10着 1:42.5
 2. 2024/09/17 金沢 ダート 1400m 良   7着 1:35.7
 3. 2024/09/03 金沢 ダート 1400m 重  12着 1:36.6
```

### 5.2 ジョッキー情報（ジョッキーID: 01157）

**累計成績:**
- 総騎乗回数: 7,573
- 1着: 582
- 勝率: 7.7%
- 連対率: 16.1%
- 複勝率: 24.5%

**直近5年成績:**
- 総騎乗回数: 627
- 1着: 52
- 勝率: 8.3%
- 連対率: 17.5%
- 複勝率: 27.0%

---

## 6. 注意事項

1. **競走成績ページ**: 馬の詳細な競走成績は `/horse/result/{horse_id}` にある
2. **血統ページ**: 親馬情報は `/horse/ped/{horse_id}` にある
3. **年度判定**: ジョッキーの年度行は `20\d{2}` の正規表現でマッチ
4. **エラーハンドリング**: データが存在しない場合の空値処理を適切に実装
5. **レート制限**: 複数ページにアクセスするため、適切な待機時間を設定

---

## 7. 次のステップ

1. `scraper/horse.py` に修正を適用
2. `scraper/jockey.py` に修正を適用
3. 既存のテストコードを更新
4. 統合テストを実行して動作確認
