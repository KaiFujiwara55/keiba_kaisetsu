# Scraper調査結果

## 問題の原因

[race.py:35](../scraper/race.py#L35)の`fetch_races_by_date`メソッドは **間違ったURL** を使用しています。

### 現在のコード（動作しない）
```python
url = f"{self.BASE_URL}/top/race_list.html?kaisai_date={date}"
```

このURLはJavaScriptで動的にレースデータを読み込むページで、初期HTMLには`.RaceList_DataList`要素やrace_idリンクが含まれていません。

## 調査結果

### 1. 初期ページ（race_list.html）
- **URL**: `https://race.netkeiba.com/top/race_list.html?kaisai_date=20251018`
- **問題**:
  - `.RaceList_DataList`要素: **0個**
  - race_idを含むリンク: **0個**
  - レースデータはJavaScriptで動的に読み込まれる

### 2. 正しいエンドポイント（race_list_sub.html）
- **URL**: `https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=20251018`
- **結果**:
  - `.RaceList_DataList`要素: **3個**（東京、京都、新潟）
  - race_idを含むリンク: **72個**
  - すべてのレースデータが含まれている

### 3. HTML構造

正しい構造:
```html
<dl class="RaceList_DataList">
    <dt class="RaceList_DataHeader">
        <div class="RaceList_DataHeader_Top">
            <p class="RaceList_DataTitle"><small>4回</small> 東京 <small>6日目</small></p>
        </div>
    </dt>
    <dd class="RaceList_Data">
        <ul>
            <li class="RaceList_DataItem">
                <a href="../race/result.html?race_id=202505040601&rf=race_list">
                    1R2歳未勝利10:05ダ1600m11頭
                </a>
            </li>
            ...
        </ul>
    </dd>
</dl>
```

### 4. セレクタの問題

現在のコード:
```python
# Line 45
race_list_sections = soup.select('.RaceList_DataList')

# Line 49
track_header = section.find_previous('div', class_='RaceList_Title')
```

問題点:
- URLは間違っているが、セレクタ`.RaceList_DataList`自体は正しい
- しかし、`find_previous('div', class_='RaceList_Title')`は間違い
  - 正: `<p class="RaceList_DataTitle">`（`<dl>`の中にある）
  - 誤: `<div class="RaceList_Title">`（存在しない）

## 解決策

### 修正が必要な箇所

1. **[race.py:35](../scraper/race.py#L35)** - URLを変更
   ```python
   # 修正前
   url = f"{self.BASE_URL}/top/race_list.html?kaisai_date={date}"

   # 修正後
   url = f"{self.BASE_URL}/top/race_list_sub.html?kaisai_date={date}"
   ```

2. **[race.py:49-52](../scraper/race.py#L49-L52)** - トラック名の取得方法を変更
   ```python
   # 修正前
   track_header = section.find_previous('div', class_='RaceList_Title')
   track_name = ""
   if track_header:
       track_name = self.safe_extract_text(track_header, 'h3', '')

   # 修正後
   track_header = section.find('dt', class_='RaceList_DataHeader')
   track_name = ""
   if track_header:
       track_name = self.safe_extract_text(track_header, '.RaceList_DataTitle', '')
   ```

3. **[race.py:75](../scraper/race.py#L75)** - レース名の取得（確認が必要）
   ```python
   # 現在のコード
   race_name = self.safe_extract_text(race_item, '.RaceName', '')

   # 確認: .RaceNameではなく.RaceList_ItemTitleの可能性
   ```

## テスト方法

修正後、以下のスクリプトでテスト可能:
```python
from scraper.race import RaceScraper

scraper = RaceScraper()
races = scraper.fetch_races_by_date("20251018")
print(f"Found {len(races)} races")
for race in races[:5]:
    print(race)
```

期待される結果: 30個以上のレース（東京12R、京都12R、新潟12Rなど）
