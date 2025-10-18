# fetch_race_details 調査結果

## 調査対象
- **関数**: `fetch_race_details` in [scraper/race.py:106](../../scraper/race.py#L106)
- **テストURL**: `https://race.netkeiba.com/race/shutuba.html?race_id=202505040704`
- **調査日**: 2025-10-18

## 問題の症状

`fetch_race_details`関数が以下のような空の結果を返す：
```json
{
  "race_id": "202505040704",
  "race_name": "2歳新馬",
  "distance": "",
  "track_type": "",
  "horses": []
}
```

- レース名は取得できている
- 距離、トラックタイプ、馬リストが空

## 原因分析

### 1. 馬リストのセレクタが間違っている

**[race.py:158](../../scraper/race.py#L158)**

❌ **現在のコード**:
```python
horse_rows = soup.select('.HorseList tr')
```

このセレクタは「`.HorseList`クラスを持つ要素の中の`tr`要素」を探していますが、実際のHTML構造は：

```html
<tr class="HorseList" id="tr_24">
  <td class="Waku1 Txt_C">...</td>
  <td class="Umaban1 Txt_C">...</td>
  <td class="HorseInfo">...</td>
  ...
</tr>
```

つまり、`tr`要素自体が`.HorseList`クラスを持っています。

✅ **正しいセレクタ**:
```python
horse_rows = soup.select('tr.HorseList')
```

**検証結果**:
- `.HorseList tr`: 0件ヒット ❌
- `tr.HorseList`: 18件ヒット ✅

---

### 2. 枠番・馬番のセレクタが間違っている

**[race.py:166-167](../../scraper/race.py#L166-L167)**

❌ **現在のコード**:
```python
frame_number_elem = row.select_one('.Waku')
horse_number_elem = row.select_one('.Umaban')
```

実際のHTMLでは、クラス名に番号が付いています：

```html
<td class="Waku1 Txt_C">
  <span>1</span>
</td>
<td class="Umaban1 Txt_C">
  1
</td>
```

✅ **正しいセレクタ**:
```python
frame_number_elem = row.select_one('td[class^="Waku"]')
horse_number_elem = row.select_one('td[class^="Umaban"]')
```

または、より安全な方法：
```python
# Waku1, Waku2, ... Waku8 のいずれかにマッチ
frame_number_elem = row.select_one('td[class*="Waku"]')
horse_number_elem = row.select_one('td[class*="Umaban"]')
```

**注意**: テキスト抽出時も修正が必要
```python
# 現在のコード（間違い）
frame_number = int(self.safe_extract_text(row, '.Waku', '0') or '0')
horse_number = int(self.safe_extract_text(row, '.Umaban', '0') or '0')

# 正しいコード
frame_number = int(self.safe_extract_text(row, 'td[class^="Waku"]', '0') or '0')
horse_number = int(self.safe_extract_text(row, 'td[class^="Umaban"]', '0') or '0')
```

---

### 3. 馬情報のセレクタが間違っている

**[race.py:176](../../scraper/race.py#L176)**

❌ **現在のコード**:
```python
horse_link = row.select_one('.Horse_Info a')
```

実際のHTMLでは、クラス名が`HorseInfo`（アンダースコアなし）：

```html
<td class="HorseInfo">
  <div>
    <div>
      <span class="HorseName">
        <a href="https://db.netkeiba.com/horse/2023106994" target="_blank" title="ティルベリー">
          ティルベリー
        </a>
      </span>
    </div>
  </div>
</td>
```

✅ **正しいセレクタ（複数の選択肢）**:
```python
# オプション1: HorseInfoから探す
horse_link = row.select_one('.HorseInfo a')

# オプション2: より具体的に
horse_link = row.select_one('.HorseName a')

# オプション3: 最も安全（どちらでも動作）
horse_link = row.select_one('.HorseInfo a, .HorseName a')
```

推奨: `.HorseInfo a` (より上位の要素を使う方が安全)

---

### 4. 距離・トラックタイプのパース問題

**[race.py:137-154](../../scraper/race.py#L137-L154)**

現在のコードは`.RaceData01`のテキスト全体を取得して`/`で分割していますが、実際のHTML構造：

```html
<div class="RaceData01">
  11:20発走 /
  <!-- <span class="Turf"> -->
  <span>ダ1600m</span>
  (左)
  / 天候:曇
  <span class="Icon_Weather Weather02"></span>
  <span class="Item04">/ 馬場:良</span>
</div>
```

テキストを取得すると：
```
11:20発走 /ダ1600m(左)/ 天候:曇/ 馬場:良
```

✅ **改善案1: 現在のアプローチを修正**

```python
race_data = self.safe_extract_text(soup, '.RaceData01', '')

distance = ""
track_type = ""

if race_data:
    # 正規表現で距離とトラックタイプを抽出
    import re

    # パターン: 芝1600m, ダ1600m, ダート1600m など
    match = re.search(r'(芝|ダート|ダ)(\d+m)', race_data)
    if match:
        track_type_raw = match.group(1)
        distance = match.group(2)

        if track_type_raw in ['芝']:
            track_type = '芝'
        elif track_type_raw in ['ダート', 'ダ']:
            track_type = 'ダート'
```

✅ **改善案2: spanタグから直接取得（より確実）**

```python
# RaceData01内のspanタグを探す
race_data_elem = soup.select_one('.RaceData01')
if race_data_elem:
    # 最初のspanタグに距離情報がある
    distance_span = race_data_elem.find('span')
    if distance_span:
        distance_text = distance_span.get_text(strip=True)  # "ダ1600m"

        # トラックタイプと距離を分離
        if '芝' in distance_text:
            track_type = '芝'
            distance = distance_text.replace('芝', '').strip()
        elif 'ダ' in distance_text:
            track_type = 'ダート'
            distance = distance_text.replace('ダート', '').replace('ダ', '').strip()
```

推奨: **改善案2**（HTMLの構造に依存しているが、より確実）

---

## 修正コード

### 完全な修正版 fetch_race_details

```python
def fetch_race_details(self, race_id: str) -> Optional[Dict]:
    """
    Fetch detailed information about a specific race

    Args:
        race_id: Race identifier (12-digit string)

    Returns:
        Dictionary containing race details and horse information
    """
    url = f"{self.BASE_URL}/race/shutuba.html?race_id={race_id}"

    soup = self.fetch(url)
    if not soup:
        return None

    # Extract race metadata
    race_name = self.safe_extract_text(soup, '.RaceName', '')

    # Extract distance and track type
    distance = ""
    track_type = ""

    race_data_elem = soup.select_one('.RaceData01')
    if race_data_elem:
        # 最初のspanタグに距離情報がある
        distance_span = race_data_elem.find('span')
        if distance_span:
            distance_text = distance_span.get_text(strip=True)  # "ダ1600m"

            # トラックタイプと距離を分離
            if '芝' in distance_text:
                track_type = '芝'
                distance = distance_text.replace('芝', '').strip()
            elif 'ダ' in distance_text:
                track_type = 'ダート'
                distance = distance_text.replace('ダート', '').replace('ダ', '').strip()

    # Extract horse entries
    horses = []
    horse_rows = soup.select('tr.HorseList')  # 修正: '.HorseList tr' -> 'tr.HorseList'

    for row in horse_rows:
        # Skip header rows
        if row.find('th'):
            continue

        # Extract frame and horse numbers
        frame_number_elem = row.select_one('td[class^="Waku"]')  # 修正
        horse_number_elem = row.select_one('td[class^="Umaban"]')  # 修正

        if not frame_number_elem or not horse_number_elem:
            continue

        frame_number = int(frame_number_elem.get_text(strip=True) or '0')
        horse_number = int(horse_number_elem.get_text(strip=True) or '0')

        # Extract horse info
        horse_link = row.select_one('.HorseInfo a')  # 修正: '.Horse_Info a' -> '.HorseInfo a'
        if not horse_link:
            continue

        horse_name = horse_link.get_text(strip=True)
        horse_id = self._extract_id_from_url(horse_link.get('href', ''), 'horse')

        # Extract jockey info
        jockey_link = row.select_one('.Jockey a')
        jockey_name = ""
        jockey_id = ""

        if jockey_link:
            jockey_name = jockey_link.get_text(strip=True)
            jockey_id = self._extract_id_from_url(jockey_link.get('href', ''), 'jockey')

        horses.append({
            'horse_id': horse_id,
            'horse_name': horse_name,
            'jockey_id': jockey_id,
            'jockey_name': jockey_name,
            'frame_number': frame_number,
            'horse_number': horse_number
        })

    return {
        'race_id': race_id,
        'race_name': race_name,
        'distance': distance,
        'track_type': track_type,
        'horses': horses
    }
```

---

## テスト結果

### 修正前
```json
{
  "race_id": "202505040704",
  "race_name": "2歳新馬",
  "distance": "",
  "track_type": "",
  "horses": []
}
```

### 修正後（期待される結果）
```json
{
  "race_id": "202505040704",
  "race_name": "2歳新馬",
  "distance": "1600m",
  "track_type": "ダート",
  "horses": [
    {
      "horse_id": "2023106994",
      "horse_name": "ティルベリー",
      "jockey_id": "05386",
      "jockey_name": "戸崎圭",
      "frame_number": 1,
      "horse_number": 1
    },
    ...（18頭分）
  ]
}
```

---

## 修正箇所まとめ

1. **[race.py:158](../../scraper/race.py#L158)** - 馬リストセレクタ
   - `'.HorseList tr'` → `'tr.HorseList'`

2. **[race.py:166-167](../../scraper/race.py#L166-L167)** - 枠番・馬番セレクタ
   - `'.Waku'` → `'td[class^="Waku"]'`
   - `'.Umaban'` → `'td[class^="Umaban"]'`

3. **[race.py:172-173](../../scraper/race.py#L172-L173)** - 枠番・馬番テキスト抽出
   - セレクタを上記に合わせて修正、またはelemから直接取得

4. **[race.py:176](../../scraper/race.py#L176)** - 馬情報セレクタ
   - `'.Horse_Info a'` → `'.HorseInfo a'`

5. **[race.py:137-154](../../scraper/race.py#L137-L154)** - 距離・トラックタイプ抽出
   - spanタグから直接取得する方法に変更

---

## 関連ファイル

- [debug_race_details.py](debug_race_details.py) - デバッグスクリプト
- [race_details_html.html](race_details_html.html) - 取得したHTML（参照用）

---

## 類似の過去問題

[debug/race_data_scraping_problem/FINDINGS.md](../race_data_scraping_problem/FINDINGS.md)でも同様の問題（セレクタの不一致）が報告されています。

netkeibaのHTML構造は想定と異なる場合が多いため、実際のHTMLを確認してからセレクタを決定することが重要です。
