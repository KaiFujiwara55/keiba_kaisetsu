## 問題
馬の情報、ジョッキーの情報が正しくスクレイピングできていない

## 馬の情報
### 情報元
取得URL: https://db.netkeiba.com/horse/{horse_id}
ex: https://db.netkeiba.com/horse/2023100452

### 取得情報
- 通算成績
- 親馬(horse_id)

## ジョッキーの情報
### 情報元
取得URL: https://db.netkeiba.com/jockey/{jockey_id}
ex: https://db.netkeiba.com/jockey/01157

### 取得情報
- 直近5年成績
    - 累計勝率
    - 累計連帯率
    - 累計複勝率

## 要望
指定したURLを実際に叩くテストコードを作成して、馬の情報、ジョッキーの情報を正しくできるスクレイピングコードを考えて。
そして、どのようにscraper配下のスクレイピングコードを書き換えるかを考えて。

## 注意
テストコードなどのdebugに使用するために作成するファイルはこのファイルのあるフォルダに配置して。
