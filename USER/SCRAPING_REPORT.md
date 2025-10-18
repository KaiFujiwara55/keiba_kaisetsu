# netkeibaでの取得情報

---
## レースID
### 前提情報
- 開催日時(race_date)
- 競馬場(東京/京都/新潟)
- レース番号

### url
https://race.netkeiba.com/top/?kaisai_date={race_date}
ex: https://race.netkeiba.com/top/?kaisai_date=20251019

### 取得情報
- race_id

---

## レース情報
### 前提情報
- race_id

### url
https://race.netkeiba.com/race/shutuba.html?race_id={race_id}&rf=race_list
ex: https://race.netkeiba.com/race/shutuba.html?race_id=202505040701&rf=race_list

### 取得情報
- 走行距離
- 芝/ダート/障害
- 馬名
- netkeibaでの馬ID(horse_id)
- 馬番
- 枠
- 斤量
- 騎手名
- netkeibaでの騎手ID(jockey_id)

----

## 馬情報
### 前提情報
- horse_id

### url
https://db.netkeiba.com/horse/{horse_id}
ex: https://db.netkeiba.com/horse/2023102602

### 取得情報
#### 出走馬のみ
- 前走との期間

#### 親馬・出走馬
- 過去レースの全戦績
    - 順位
    - タイム

---

## 騎手情報
### 前提情報
- jockey_id

### url
https://db.netkeiba.com/jockey/{jockey_id}
ex: https://db.netkeiba.com/jockey/01214

### 取得情報
- 直近5年成績
    - 勝率
    - 複勝率
