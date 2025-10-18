# Streamlit Cloud デプロイ手順書

このドキュメントでは、競馬レース解析アプリをStreamlit Cloudにデプロイする手順を説明します。

## 📋 前提条件

- GitHubアカウント
- AWSアカウント（無料利用枠でOK）
- ローカルにAWS CLIがインストール済み

---

## 🚀 デプロイ手順

### ステップ1: AWSアカウントの準備

#### 1-1. AWSアカウント作成

1. https://aws.amazon.com/jp/ にアクセス
2. 「AWSアカウントを作成」をクリック
3. メールアドレス、パスワード、アカウント名を入力
4. 連絡先情報を入力
5. クレジットカード情報を登録（無料利用枠内でも必須）
6. 電話番号認証を完了
7. サポートプラン「ベーシックプラン（無料）」を選択

#### 1-2. IAMユーザー作成（推奨）

1. AWSマネジメントコンソールにログイン
2. IAMサービスを開く
3. 「ユーザー」→「ユーザーを作成」
4. ユーザー名を入力（例：`admin-user`）
5. 以下の権限をアタッチ：
   - `AdministratorAccess`（初期設定用、後で削除）
6. 「セキュリティ認証情報」→「アクセスキーを作成」
7. 用途：「コマンドラインインターフェイス(CLI)」
8. アクセスキーIDとシークレットアクセスキーをメモ

#### 1-3. AWS CLIの設定

```bash
# AWS CLIのインストール（macOS）
brew install awscli

# 認証情報の設定
aws configure
# AWS Access Key ID: (取得したアクセスキーID)
# AWS Secret Access Key: (取得したシークレットアクセスキー)
# Default region name: ap-northeast-1
# Default output format: json

# 確認
aws sts get-caller-identity
```

---

### ステップ2: AWS環境のセットアップ

#### 2-1. DynamoDBテーブルの作成

```bash
source venv/bin/activate
python scripts/setup_dynamodb.py
```

成功すると以下のメッセージが表示されます：
```
✅ テーブル 'keiba_cache' の作成が完了しました。
```

#### 2-2. Streamlit用IAMユーザーの作成

```bash
source venv/bin/activate
python scripts/create_limited_iam_user.py
```

出力されたアクセスキー情報を**必ず保存**してください：

```toml
[aws]
region = "ap-northeast-1"
access_key_id = "AKIA..."
secret_access_key = "xxx..."

[dynamodb]
table_name = "keiba_cache"
```

⚠️ **重要**: このシークレットアクセスキーは二度と表示されません。安全な場所に保存してください。

---

### ステップ3: ローカルでのテスト

#### 3-1. secrets.tomlの作成

```bash
# テンプレートをコピー
cp .streamlit/secrets.toml.template .streamlit/secrets.toml

# エディタで編集
code .streamlit/secrets.toml
# または
nano .streamlit/secrets.toml
```

以下の情報を入力：

```toml
# AWS認証情報（ステップ2-2で取得）
[aws]
region = "ap-northeast-1"
access_key_id = "AKIA..."
secret_access_key = "xxx..."

# DynamoDB設定
[dynamodb]
table_name = "keiba_cache"

# アプリケーションパスワード
APP_PASSWORD = "your-secure-password"

# LLM API Keys
OPENAI_API_KEY = "sk-proj-..."  # OpenAI APIキー
ANTHROPIC_API_KEY = "sk-ant-..."  # Anthropic APIキー

# 使用するアナライザー
ANALYZER_TYPE = "claude"  # または "gpt"
```

#### 3-2. ローカルで起動

```bash
source venv/bin/activate
streamlit run app.py
```

ブラウザで http://localhost:8501 が開きます。

動作確認：
- ログイン画面が表示されるか
- パスワードでログインできるか
- レース一覧が取得できるか
- 解析が動作するか

---

### ステップ4: GitHubへのプッシュ

#### 4-1. リポジトリの確認

```bash
# 変更を確認
git status

# secrets.tomlがGitに含まれていないことを確認
git status | grep secrets.toml
# → 何も表示されなければOK
```

#### 4-2. コミットとプッシュ

```bash
# 変更をステージング
git add .

# コミット
git commit -m "Add Streamlit Cloud deployment support"

# プッシュ（メインブランチの場合）
git push origin main
```

---

### ステップ5: Streamlit Cloudへのデプロイ

#### 5-1. Streamlit Cloudにサインアップ

1. https://share.streamlit.io/ にアクセス
2. 「Sign up」をクリック
3. GitHubアカウントでサインアップ

#### 5-2. アプリのデプロイ

1. 「New app」をクリック
2. 以下を入力：
   - **Repository**: あなたのGitHubリポジトリを選択
   - **Branch**: `main`（またはデプロイしたいブランチ）
   - **Main file path**: `app.py`
3. 「Advanced settings」をクリック
4. **Python version**: `3.11` を選択
5. 「Deploy」をクリック

#### 5-3. Secretsの設定

デプロイ後、Secretsを設定します：

1. アプリのダッシュボードを開く
2. 右上の「⚙️」（Settings）をクリック
3. 左メニューから「Secrets」を選択
4. ローカルの `.streamlit/secrets.toml` の内容を**全てコピーして貼り付け**
5. 「Save」をクリック
6. 「Reboot app」をクリック（アプリを再起動）

```toml
# この内容をStreamlit CloudのSecretsに貼り付け
[aws]
region = "ap-northeast-1"
access_key_id = "AKIA..."
secret_access_key = "xxx..."

[dynamodb]
table_name = "keiba_cache"

APP_PASSWORD = "your-secure-password"
OPENAI_API_KEY = "sk-proj-..."
ANTHROPIC_API_KEY = "sk-ant-..."
ANALYZER_TYPE = "claude"
```

#### 5-4. デプロイ完了

数分後、アプリが起動します。

アプリURL: `https://あなたのアプリ名.streamlit.app`

---

## 🔧 トラブルシューティング

### エラー: ModuleNotFoundError

**原因**: 必要なライブラリがインストールされていない

**解決策**:
1. `requirements.txt` を確認
2. Streamlit Cloudで「Reboot app」を実行

### エラー: DynamoDB connection failed

**原因**: AWS認証情報が正しくない、またはSecretsが設定されていない

**解決策**:
1. Streamlit CloudのSecretsを確認
2. AWSアクセスキーが正しいか確認
3. DynamoDBテーブルが作成されているか確認
   ```bash
   aws dynamodb describe-table --table-name keiba_cache
   ```

### エラー: API key not found

**原因**: LLM APIキーがSecretsに設定されていない

**解決策**:
1. Streamlit CloudのSecretsに `OPENAI_API_KEY` または `ANTHROPIC_API_KEY` を追加
2. 「Reboot app」を実行

### アプリがスリープする

Streamlit Community Cloudの無料プランでは、アクセスがないとアプリがスリープします。

**対策**:
- アクセスすれば自動的に再起動します（初回は少し時間がかかります）
- 常時起動が必要な場合は有料プランを検討

---

## 🗑️ クリーンアップ（削除手順）

### Streamlit Cloudからアプリを削除

1. Streamlit Cloudのダッシュボードを開く
2. アプリの「⚙️」→「Settings」
3. 「Delete app」をクリック

### AWSリソースの削除

```bash
source venv/bin/activate

# DynamoDBテーブルを削除
python scripts/setup_dynamodb.py delete

# IAMユーザーを削除
python scripts/create_limited_iam_user.py delete
```

または、AWSマネジメントコンソールから手動で削除：
1. DynamoDB: テーブル `keiba_cache` を削除
2. IAM: ユーザー `streamlit-keiba-user` を削除

---

## 💰 コスト見積もり

### AWS無料枠内での利用

**完全無料で使える条件**:
- DynamoDB: 月250万読み取り、25万書き込み（12ヶ月間）
- データ転送: 月1GB（永続無料）
- 想定利用: 月1000回の解析 → **$0**

### LLM APIコスト

**Claude 3.5 Sonnet**（推奨）:
- 1回の解析: 約$0.04-0.06（5-8円）
- 月1000回: 約$40-60（5,000-8,000円）

**GPT-4**:
- 1回の解析: 約$0.05-0.08（7-11円）
- 月1000回: 約$50-80（7,000-11,000円）

**節約のコツ**:
- キャッシュ機能を活用（同じレース・同じプロンプトなら再利用）
- 必要なレースのみ解析

---

## 📚 参考リンク

- [Streamlit Cloud ドキュメント](https://docs.streamlit.io/streamlit-community-cloud)
- [AWS DynamoDB 無料利用枠](https://aws.amazon.com/jp/dynamodb/pricing/)
- [Anthropic Claude API](https://www.anthropic.com/api)
- [OpenAI API](https://platform.openai.com/)

---

## 🆘 サポート

問題が発生した場合:
1. このREADMEのトラブルシューティングを確認
2. ログを確認（Streamlit Cloudの「Manage app」→「Logs」）
3. GitHubのIssuesで質問

---

**デプロイ成功をお祈りします！ 🎉**
