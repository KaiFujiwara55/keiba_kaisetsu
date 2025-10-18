# 馬・ジョッキーデータ取得問題の修正

## 問題の概要

アプリで馬とジョッキーの成績データが正しく取得できていませんでした。

### 発見された問題

1. **馬の過去成績データが空**
   - `recent_results` が常に空の配列
   - `days_since_last_race` が常に999

2. **ジョッキーの勝率・連対率が0**
   - `jockey_win_rate` が常に0
   - `jockey_place_rate` が常に0

3. **馬の過去成績の各フィールドに異なるデータが入っている**
   - `distance` に天気（"晴"）が入っている
   - `time` にレース名（"2歳新馬"）が入っている
   - `position` に正しくない値が入っている

4. **親馬の獲得賞金と成績が空**
   - `sire_earnings`, `sire_record` が常に空文字列
   - `dam_earnings`, `dam_record` が常に空文字列

## 原因分析

### 1. 馬の成績データ - 誤ったURL（horse.py 41行目）

**問題点:**
```python
# 誤ったURL
url = f"{self.BASE_URL}/horse/{horse_id}/"
```

このURLではレース結果テーブル (`.db_h_race_results`) が存在しない。

**修正:**
```python
# 正しいURL
url = f"{self.BASE_URL}/horse/result/{horse_id}/"
```

### 2. 馬の成績データ - 列の位置がずれている（horse.py 63-96行目）

**問題点:**
HTMLテーブルの列の位置が実際の構造と異なっていた。

実際のHTML構造：
```
Column 0:  日付
Column 1:  開催（トラック）
Column 2:  天気
Column 3:  R
Column 4:  レース名
Column 11: 着順
Column 14: 距離
Column 18: タイム
Column 19: 着差
```

旧コードは以下のように誤った列を参照していた：
```python
distance_data = self.safe_extract_text(row, 'td:nth-of-type(3)', '')  # 天気を取得
position_str = self.safe_extract_text(row, 'td:nth-of-type(4)', '0')  # Rを取得
time_str = self.safe_extract_text(row, 'td:nth-of-type(5)', '')       # レース名を取得
```

**修正:**
```python
# 距離（Column 14）
distance_data = self.safe_extract_text(row, 'td:nth-of-type(15)', '')

# 着順（Column 11）
position_str = self.safe_extract_text(row, 'td:nth-of-type(12)', '0')

# タイム（Column 18）
time_str = self.safe_extract_text(row, 'td:nth-of-type(19)', '')

# 着差（Column 19）
margin = self.safe_extract_text(row, 'td:nth-of-type(20)', '')
```

### 3. ジョッキーの統計データ（app.py 106-113行目）

**問題点:**
`JockeyScraper.fetch_jockey_stats()` は以下の構造を返す：
```python
{
    'jockey_id': '...',
    'jockey_name': '...',
    'overall_stats': {
        'win_rate': 22.1,
        'place_rate': 38.1,
        ...
    },
    'recent_5year_stats': {...}
}
```

しかしapp.pyでは直接アクセスしていた：
```python
# 誤ったアクセス
'jockey_win_rate': jockey_stats.get('win_rate', 0)  # 常に0
'jockey_place_rate': jockey_stats.get('place_rate', 0)  # 常に0
```

**修正:**
```python
# 正しいアクセス
jockey_overall_stats = jockey_stats.get('overall_stats', {}) if jockey_stats else {}
'jockey_win_rate': jockey_overall_stats.get('win_rate', 0)
'jockey_place_rate': jockey_overall_stats.get('place_rate', 0)
```

### 4. 親馬のデータ（app.py 115-119行目）

**問題点:**
`HorseScraper.fetch_parent_horses()` は `name` と `id` しか返さない：
```python
{
    'sire': {'name': '...', 'id': '...'},
    'dam': {'name': '...', 'id': '...'}
}
```

しかしapp.pyでは `earnings` と `record` にもアクセスしようとしていた。

**修正:**
これらのフィールドを取得するには親馬のIDを使って別途APIコールが必要だが、
パフォーマンスへの影響を考慮して、現時点では空文字列を設定：
```python
'sire_earnings': '',  # Not currently fetched
'sire_record': '',    # Not currently fetched
'dam_earnings': '',   # Not currently fetched
'dam_record': '',     # Not currently fetched
```

## 修正ファイル

1. **[scraper/horse.py](../../scraper/horse.py)**
   - 41行目: URLを `/horse/{horse_id}/` から `/horse/result/{horse_id}/` に修正
   - 63-96行目: 列の位置を修正（distance: 15, position: 12, time: 19, margin: 20）

2. **[app.py](../../app.py)**
   - 106-113行目: ジョッキー統計のアクセス方法を修正
   - 115-119行目: 親馬のデータアクセスを修正（現在は空文字列）

## テスト結果

### 修正前
```json
{
  "date": "2025/08/31",
  "track": "3新潟4",
  "distance": "晴",           // ❌ 天気が入っている
  "position": 6,              // ❌ レース番号が入っている
  "time": "2歳新馬",          // ❌ レース名が入っている
  "margin": ""
}
```

### 修正後
```json
{
  "date": "2025/08/31",
  "track": "3新潟4",
  "distance": "ダ1800",       // ✅ 正しい距離
  "position": 2,              // ✅ 正しい着順
  "time": "1:56.2",           // ✅ 正しいタイム
  "margin": "1.0"             // ✅ 正しい着差
}
```

### 完全なテスト結果

テストスクリプト `test_fixes.py` の実行結果：

```
1. Testing Horse Data (ID: 2023103793)
✓ Horse name: サイモフェーン
✓ Recent results count: 1
✓ Days since last race: 48
  Latest race result:
    Date: 2025/08/31
    Track: 3新潟4
    Distance: ダ1800
    Position: 2

2. Testing Jockey Data (ID: 05339)
✓ Jockey name: Ｃ．ルメール
✓ Overall win rate: 22.1%
✓ Overall place rate: 38.1%
✓ Total races: 9328
✓ Total wins: 2066
```

## 実行方法

```bash
# 個別テスト
source venv/bin/activate
python debug/horse_jockey_data_problem/test_fixes.py

# HTML構造の確認
python debug/horse_jockey_data_problem/check_html_structure.py

# 過去成績の詳細確認
python debug/horse_jockey_data_problem/check_recent_results.py
```

## 今後の改善案

### 親馬の獲得賞金と成績を取得する場合
1. `HorseScraper.fetch_overall_stats()` を使って親馬のIDから統計を取得
2. ただし、各馬につき2回の追加APIコールが必要（父馬・母馬）
3. パフォーマンスへの影響を考慮して実装するかを判断

### より詳細なレース情報
現在の `fetch_horse_results()` は基本的な情報のみ取得していますが、
`fetch_race_results()` メソッドを使えば以下の追加情報も取得可能：
- 天気
- 馬場状態
- 通過順位
- 上がり3F
- 馬体重
- など

## まとめ

- ✅ 馬の過去成績が正しく取得できるようになった
  - URLを修正
  - 列の位置を正しく修正
- ✅ 過去成績の各フィールドに正しいデータが入るようになった
  - `distance`: ダ1800（距離・トラックタイプ）
  - `time`: 1:56.2（タイム）
  - `position`: 2（着順）
- ✅ ジョッキーの勝率・連対率が正しく表示されるようになった
- ✅ 親馬の名前が正しく取得できている
- ⚠️ 親馬の獲得賞金と成績は現在未実装（必要に応じて今後実装）
