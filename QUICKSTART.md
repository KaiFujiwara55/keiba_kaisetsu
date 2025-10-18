# 🚀 クイックスタートガイド

このガイドでは、最短でStreamlit Cloudにデプロイする手順を説明します。

## 📝 必要なもの

- [ ] GitHubアカウント
- [ ] AWSアカウント
- [ ] OpenAI または Anthropic APIキー

---

## ⚡ 5ステップでデプロイ

### 1️⃣ AWS環境をセットアップ（10分）

```bash
# AWS CLIの設定
aws configure
# Access Key, Secret Key, Region (ap-northeast-1) を入力

# DynamoDBテーブル作成
source venv/bin/activate
python scripts/setup_dynamodb.py

# Streamlit用IAMユーザー作成
python scripts/create_limited_iam_user.py
# 👆 出力されたアクセスキーを必ずコピー！
```

### 2️⃣ ローカルでテスト（5分）

```bash
# secrets.toml作成
cp .streamlit/secrets.toml.template .streamlit/secrets.toml

# エディタで編集（APIキーを入力）
code .streamlit/secrets.toml

# 起動
streamlit run app.py
```

### 3️⃣ GitHubにプッシュ（2分）

```bash
git add .
git commit -m "Add Streamlit Cloud support"
git push origin main
```

### 4️⃣ Streamlit Cloudでデプロイ（5分）

1. https://share.streamlit.io/ を開く
2. 「New app」をクリック
3. リポジトリ、ブランチ、`app.py` を選択
4. 「Deploy」をクリック

### 5️⃣ Secretsを設定（3分）

1. Settings → Secrets
2. `.streamlit/secrets.toml` の内容を全てコピペ
3. 「Save」→「Reboot app」

---

## ✅ 完了！

アプリURL: `https://あなたのアプリ名.streamlit.app`

---

## 💡 よくある質問

**Q: どのくらいコストがかかりますか？**
A: AWS側は無料枠内で完全無料。LLM APIは1回5-8円程度（使った分だけ）。

**Q: プライベートで使えますか？**
A: パスワード認証があるので、パスワードを知っている人だけが使えます。

**Q: 後で削除できますか？**
A: できます。詳細は [DEPLOYMENT.md](DEPLOYMENT.md) のクリーンアップセクションを参照。

---

詳しい手順は [DEPLOYMENT.md](DEPLOYMENT.md) を参照してください。
