# 競馬レース解析アプリ

netkeibaから競馬データをスクレイピングし、AI (GPT-5 または Claude 4.5) を使用して各馬の強み・弱点を分析するWebアプリケーション。

## 機能

- **データスクレイピング**: netkeibaから出走馬、騎手、血統情報を自動取得
- **AI解析**: OpenAI GPT-5 または Anthropic Claude 4.5 による詳細な馬の分析
- **Web UI**: Streamlitベースのモバイル対応インターフェース
- **キャッシング**: DynamoDBによる高速データ取得とコスト削減
- **認証**: 簡易パスワード認証

## 必要な環境

- Python 3.12+
- AWS アカウント (DynamoDB用)
- OpenAI API キー (GPT-5アクセス用) **または** Anthropic API キー (Claude 4.5アクセス用)

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

`.streamlit/secrets.toml` を作成して必要な値を設定:

```bash
mkdir -p .streamlit
cat > .streamlit/secrets.toml << 'EOF'
# AI解析エンジンの選択 (claude または gpt)
ANALYZER_TYPE = "claude"

# Anthropic API キー (Claude使用時)
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"

# OpenAI API キー (GPT使用時)
OPENAI_API_KEY = "your-openai-api-key-here"

# アプリログインパスワード
APP_PASSWORD = "your-secure-password"

# AWS設定 (オプション: DynamoDBキャッシュを使用しない場合は不要)
AWS_REGION = "ap-northeast-1"
DYNAMODB_TABLE = "keiba_data"
EOF
```

編集が必要な環境変数:

- `ANALYZER_TYPE`: 使用するAIエンジン (`claude` または `gpt`)
- `ANTHROPIC_API_KEY`: Anthropic APIキー (Claude使用時)
- `OPENAI_API_KEY`: OpenAI APIキー (GPT使用時)
- `APP_PASSWORD`: アプリのログインパスワード
- `AWS_REGION`: DynamoDBのリージョン (オプション、デフォルト: ap-northeast-1)
- `DYNAMODB_TABLE`: DynamoDBテーブル名 (オプション、デフォルト: keiba_data)

### 5. DynamoDBテーブルを作成 (オプション)

**注意**: DynamoDBキャッシュは任意です。キャッシュなしでも動作します。

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
# venv環境をアクティベート
source venv/bin/activate

# Streamlitアプリを起動
streamlit run app.py
```

ブラウザで `http://localhost:8501` にアクセス。

## プロジェクト構成

```
keiba_kaisetsu/
├── app.py                    # Streamlitメインアプリケーション
├── requirements.txt          # Python依存パッケージ
├── Dockerfile               # Docker設定
├── scraper/                 # netkeibaスクレイピングモジュール
│   ├── base.py             # スクレイピング基底クラス
│   ├── race.py             # レース情報スクレイパー
│   ├── horse.py            # 馬情報スクレイパー
│   └── jockey.py           # 騎手情報スクレイパー
├── analyzer/               # AI解析モジュール
│   ├── gpt_analyzer.py     # GPT-5解析エンジン
│   ├── claude_analyzer.py  # Claude 4.5解析エンジン
│   └── prompts.py          # 解析用プロンプト
├── cache/                  # キャッシュモジュール
│   └── dynamodb.py         # DynamoDBキャッシュ実装
└── .streamlit/
    └── secrets.toml        # 環境変数設定
```

## Streamlit Cloudデプロイ (推奨)

### 1. 前提条件

- GitHubアカウント
- AWSアカウント (DynamoDBキャッシュ使用時、無料枠でOK)
- ローカルにAWS CLIがインストール済み

### 2. AWS環境のセットアップ (DynamoDBキャッシュ使用時)

```bash
# DynamoDBテーブルの作成
source venv/bin/activate
python scripts/setup_dynamodb.py

# Streamlit用IAMユーザーの作成
python scripts/create_limited_iam_user.py
```

出力されたアクセスキー情報を保存してください。

### 3. GitHubへプッシュ

```bash
# 変更をコミット
git add .
git commit -m "Add Streamlit Cloud deployment support"
git push origin main
```

### 4. Streamlit Cloudでデプロイ

1. https://share.streamlit.io/ にアクセス
2. GitHubアカウントでサインアップ
3. 「New app」をクリック
4. リポジトリ、ブランチ、メインファイル (`app.py`) を選択
5. Python version: `3.11` または `3.12` を選択
6. 「Deploy」をクリック

### 5. Secretsの設定

デプロイ後、アプリの設定画面でSecretsを設定:

1. アプリのダッシュボード → 「⚙️ Settings」 → 「Secrets」
2. `.streamlit/secrets.toml` の内容をコピー&ペースト:

```toml
# AWS認証情報 (DynamoDBキャッシュ使用時)
[aws]
region = "ap-northeast-1"
access_key_id = "AKIA..."
secret_access_key = "xxx..."

[dynamodb]
table_name = "keiba_cache"

# アプリケーション設定
APP_PASSWORD = "your-secure-password"
ANALYZER_TYPE = "claude"  # または "gpt"

# API Keys
ANTHROPIC_API_KEY = "sk-ant-..."  # Claude使用時
OPENAI_API_KEY = "sk-proj-..."     # GPT使用時
```

3. 「Save」→「Reboot app」で再起動

### 6. デプロイ完了

アプリURL: `https://あなたのアプリ名.streamlit.app`

詳細な手順は [DEPLOYMENT.md](DEPLOYMENT.md) を参照してください。

## 使い方

1. **ログイン**: 設定したパスワードでログイン
2. **レース日選択**: 分析したいレースの日付を選択
3. **レース取得**: "レース一覧を取得"ボタンをクリック
4. **レース選択**: 競馬場とレース番号を選択
5. **カスタムプロンプト**: (オプション) 追加の分析指示を入力
6. **キャッシュ設定**: キャッシュを利用するか新規生成するかを選択
7. **解析開始**: "🚀 解析開始"ボタンをクリック
8. **結果表示**: AI解析結果とトークン使用量・コストを確認

## コスト見積もり

### Claude 4.5使用時 (推奨)

**1レース解析あたり**:
- 入力トークン: 約10,000トークン × $0.003/1k = $0.03
- 出力トークン: 約5,000トークン × $0.015/1k = $0.075
- **合計**: 約$0.10-0.15/レース

**1日使用 (10レース解析想定)**:
- **AI API**: $1.00-1.50
- **AWS (DynamoDB)**: $0.10-0.30 (キャッシュ使用時)
- **合計**: 約$1.10-1.80/日

### GPT-5使用時

**1レース解析あたり**:
- 入力トークン: 約10,000トークン × $0.00150/1k = $0.015
- 出力トークン: 約5,000トークン × $0.00600/1k = $0.030
- **合計**: 約$0.045-0.06/レース

**1日使用 (10レース解析想定)**:
- **AI API**: $0.45-0.60
- **AWS (DynamoDB)**: $0.10-0.30 (キャッシュ使用時)
- **合計**: 約$0.55-0.90/日

### キャッシュの効果

- 同じレース・同じプロンプトの組み合わせは自動的にキャッシュから取得
- キャッシュヒット時はAPI料金が**0円**
- DynamoDBキャッシュは7日間有効 (TTL自動削除)

## トラブルシューティング

### DynamoDB接続エラー

- AWS認証情報が正しく設定されているか確認
- IAMロールにDynamoDBアクセス権限があるか確認
- リージョンが正しいか確認

### スクレイピングエラー

- netkeibaのHTML構造が変更された可能性
- ネットワーク接続を確認
- レート制限に達していないか確認

### AI APIエラー

**Claude APIエラーの場合**:
- `ANTHROPIC_API_KEY`が正しいか確認
- Anthropic APIの利用状況を確認
- レート制限に達していないか確認

**GPT APIエラーの場合**:
- `OPENAI_API_KEY`が正しいか確認
- トークン制限を超えていないか確認
- OpenAI APIの利用状況を確認

## 制限事項

- スクレイピング対象: netkeiba.com のみ
- スクレイピング頻度: ネットワークに負荷をかけないよう適切な間隔で使用してください
- キャッシュ期間: 7日間 (DynamoDB TTL自動削除)
- 認証: 簡易パスワード認証のみ (本番環境ではより強固な認証を推奨)

## 技術スタック

- **フロントエンド**: Streamlit
- **スクレイピング**: Beautiful Soup 4 + lxml
- **AI解析**:
  - Anthropic Claude 4.5 (anthropic SDK)
  - OpenAI GPT-5 (openai SDK)
- **キャッシュ**: AWS DynamoDB (オプション)
- **デプロイ**: Streamlit Cloud (推奨)

## データ取得について

このアプリケーションは以下のデータをnetkeibaから取得します:

1. **レース情報**:
   - レース名、競馬場、距離、馬場状態
   - 出走馬一覧と馬番、枠番

2. **馬の情報**:
   - 過去の成績 (着順、タイム、人気)
   - 前走からの間隔
   - 父馬・母馬の血統情報と成績

3. **騎手情報**:
   - 勝率、連対率、複勝率
   - 総合統計

## 開発とテスト

```bash
# テストファイルがある場合
source venv/bin/activate
pytest

# デバッグ用スクリプトの実行
python debug/race_data_fetch_problem/debug_quick.py 202508030601
```

## Docker実行 (オプション)

ローカル環境でDockerを使いたい場合のみ参照してください。

### ビルド

```bash
docker build -t keiba-app .
```

### 実行

```bash
# secrets.tomlを使用する場合
docker run -p 8501:8501 -v $(pwd)/.streamlit:/app/.streamlit keiba-app

# 環境変数で直接指定する場合
docker run -p 8501:8501 \
  -e ANALYZER_TYPE=claude \
  -e ANTHROPIC_API_KEY=your-key \
  -e APP_PASSWORD=your-password \
  keiba-app
```

**注意**: Streamlit Cloudへのデプロイには不要です。

## ライセンス

このプロジェクトは個人利用を目的としています。
netkeibaの利用規約を遵守してください。

## お問い合わせ

問題や質問がある場合は、Issueを作成してください。
