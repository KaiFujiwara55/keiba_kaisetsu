# 競馬レース解析アプリ

netkeibaから競馬データをスクレイピングし、GPT-5を使用して各馬の強み・弱点を分析するWebアプリケーション。

## 機能

- **データスクレイピング**: netkeibaから出走馬、騎手、血統情報を自動取得
- **LLM解析**: OpenAI GPT-5による詳細な馬の分析
- **Web UI**: Streamlitベースのモバイル対応インターフェース
- **キャッシング**: DynamoDBによる高速データ取得とコスト削減
- **認証**: 簡易パスワード認証

## 必要な環境

- Python 3.11+
- AWS アカウント (DynamoDB用)
- OpenAI API キー (GPT-5アクセス)

## セットアップ

### 1. リポジトリをクローン

```bash
git clone <repository-url>
cd keiba_kaisetsu
```

### 2. 仮想環境を作成

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

### 3. 依存関係をインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数を設定

`.env.example`をコピーして`.env`を作成し、必要な値を設定:

```bash
cp .env.example .env
```

編集が必要な環境変数:

- `OPENAI_API_KEY`: OpenAI APIキー
- `APP_PASSWORD`: アプリのログインパスワード
- `AWS_REGION`: DynamoDBのリージョン (デフォルト: ap-northeast-1)
- `DYNAMODB_TABLE`: DynamoDBテーブル名 (デフォルト: keiba_data)

### 5. DynamoDBテーブルを作成

AWS ConsoleまたはCLIで以下のテーブルを作成:

```bash
aws dynamodb create-table \
    --table-name keiba_data \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-1
```

TTLを有効化:

```bash
aws dynamodb update-time-to-live \
    --table-name keiba_data \
    --time-to-live-specification \
        "Enabled=true, AttributeName=ttl" \
    --region ap-northeast-1
```

### 6. ローカルで実行

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` にアクセス。

## Docker実行

### ビルド

```bash
docker build -t keiba-app .
```

### 実行

```bash
docker run -p 8501:8501 --env-file .env keiba-app
```

## AWSデプロイ (App Runner)

### 1. ECRリポジトリを作成

```bash
aws ecr create-repository --repository-name keiba-app --region ap-northeast-1
```

### 2. Dockerイメージをプッシュ

```bash
# ECRにログイン
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com

# イメージをタグ付け
docker tag keiba-app:latest <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com/keiba-app:latest

# プッシュ
docker push <account-id>.dkr.ecr.ap-northeast-1.amazonaws.com/keiba-app:latest
```

### 3. App Runnerサービスを作成

AWS Consoleで:

1. App Runnerサービスを作成
2. ソース: ECRリポジトリ
3. デプロイ設定:
   - vCPU: 0.25
   - メモリ: 0.5GB
4. 環境変数を設定:
   - `OPENAI_API_KEY`
   - `APP_PASSWORD`
   - `AWS_REGION`
   - `DYNAMODB_TABLE`
   - その他必要な変数
5. IAMロールにDynamoDBアクセス権限を追加

## 使い方

1. **ログイン**: 設定したパスワードでログイン
2. **レース日選択**: 分析したいレースの日付を選択
3. **レース取得**: "レース一覧を取得"ボタンをクリック
4. **レース選択**: 競馬場とレース番号を選択
5. **カスタムプロンプト**: (オプション) 追加の分析指示を入力
6. **解析開始**: "解析開始"ボタンをクリック
7. **結果表示**: 3つのタブで結果を確認
   - 個別馬分析
   - 馬同士の比較
   - おすすめランキング

## コスト見積もり

### 1日使用 (30レース解析想定)

- **AWS (App Runner + DynamoDB)**: $0.50-1.00
- **GPT-5 API**: $2.25
- **合計**: 約$2.75-3.25/日

### 月間使用 (数百レース解析想定)

- **AWS**: $17-40
- **GPT-5 API**: $50-100
- **合計**: 約$67-140/月

## トラブルシューティング

### DynamoDB接続エラー

- AWS認証情報が正しく設定されているか確認
- IAMロールにDynamoDBアクセス権限があるか確認
- リージョンが正しいか確認

### スクレイピングエラー

- netkeibaのHTML構造が変更された可能性
- ネットワーク接続を確認
- レート制限に達していないか確認

### GPT-5 APIエラー

- APIキーが正しいか確認
- トークン制限を超えていないか確認
- OpenAI APIの利用状況を確認

## 制限事項

- スクレイピング対象: netkeiba.com
- 同時アクセス: 小規模利用を想定 (1日30アクセス程度)
- キャッシュ期間: 7日間 (TTL自動削除)
- 認証: 簡易パスワード認証のみ

## ライセンス

このプロジェクトは個人利用を目的としています。
netkeibaの利用規約を遵守してください。

## お問い合わせ

問題や質問がある場合は、Issueを作成してください。
