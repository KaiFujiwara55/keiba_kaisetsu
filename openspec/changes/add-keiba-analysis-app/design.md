# 設計ドキュメント - 競馬レース解析アプリ

## Context

netkeibaから競馬データをスクレイピングし、GPT-5による解析を提供するStreamlitベースのWebアプリケーション。1日限定使用（30アクセス想定）だが、将来的な拡張も考慮した設計とする。

### 制約条件
- スマホからの使用を想定
- 簡易パスワード認証（ハードコード）
- AWS環境でのデプロイ
- コスト最小化（1日使用で$0.50-1.00目標）
- **調査結果**: requestsのみで実装可能（Selenium不要）

### ステークホルダー
- エンドユーザー: 競馬予想を行いたいユーザー（数名程度）

## Goals / Non-Goals

### Goals
- netkeibaから必要な競馬データを確実にスクレイピングできる
- GPT-5を使った高品質な解析結果を提供する
- スマホで使いやすいUI/UXを実現する
- スクレイピングデータをキャッシュして高速化とコスト削減を実現する
- 簡単にデプロイ・運用できる構成にする

### Non-Goals
- 複数ユーザーの同時アクセス対応（30アクセス/日程度を想定）
- 高度なユーザー管理・権限機能
- リアルタイムオッズ連携
- 過去レースの大量データ分析

## Decisions

### 1. アーキテクチャ: モノリシックStreamlitアプリ

**決定**: 単一のStreamlitアプリケーションとして実装

**理由**:
- 開発速度が速い（1ファイルまたは少数ファイルで完結可能）
- Streamlitは状態管理が容易
- 小規模アクセスには十分
- デプロイが簡単

**代替案**:
- FastAPI + React: 複雑すぎる、開発時間がかかる
- Django: オーバーキル、不要な機能が多い

### 2. スクレイピング: requests + BeautifulSoup4

**決定**: requestsでHTTP取得 + BeautifulSoup4でパース

**理由**:
- **実測調査の結果**: netkeibaの全ページが静的HTMLで提供されている
- JavaScriptレンダリング不要
- 軽量で高速
- Dockerイメージが小さい（Seleniumの場合+300MB程度）
- 実装がシンプル

**代替案の検討**:
- Selenium: 不要（実測で静的HTML確認済み）
- Playwright: オーバースペック
- Scrapy: フレームワークは不要

**実装詳細**:
```python
import requests
from bs4 import BeautifulSoup

class NetkeibaScraper:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    def fetch(self, url):
        response = requests.get(url, headers=self.HEADERS, timeout=10)
        response.encoding = response.apparent_encoding  # 自動検出
        return BeautifulSoup(response.text, 'html.parser')
```

**パフォーマンス見積もり**:
- 1レースあたり: 50-74リクエスト（平均60）
  - レースID取得: 1
  - レース詳細: 1
  - 馬情報: 15頭
  - 親馬情報: 30（父母）
  - 騎手情報: 15
- 処理時間: 30-60秒（キャッシュなし）、10-20秒（キャッシュあり）

### 3. データベース: DynamoDB (Single Table Design)

**決定**: DynamoDB単一テーブルで全データを管理

**スキーマ設計**:
```
Table: keiba_data

Primary Key:
  PK (Partition Key): String
  SK (Sort Key): String

Attributes:
  - data: Map (実際のデータ)
  - fetched_at: Number (UnixTimestamp)
  - ttl: Number (TTL用、7日後に自動削除)

アクセスパターン:
1. レース情報取得
   PK: RACE#{race_id}
   SK: METADATA
   data: { distance, track_type, horses: [...] }

2. 馬の過去成績取得
   PK: HORSE#{horse_id}
   SK: RESULTS
   data: { results: [...] }

3. 親馬情報取得
   PK: HORSE#{horse_id}
   SK: PARENT
   data: { sire: {...}, dam: {...} }

4. 騎手情報取得
   PK: JOCKEY#{jockey_id}
   SK: STATS
   data: { win_rate, place_rate, ... }
```

**理由**:
- 無料枠が大きい（25GB、読み取り・書き込み多数）
- サーバーレス（管理不要）
- TTL機能でキャッシュ自動削除（7日間）
- Single Table Designでコスト最適化
- AWSエコシステムとの統合が容易

**代替案**:
- MongoDB Atlas: 無料枠が小さい（512MB）、別サービス管理
- RDS: コストが高い（最小でも$10-15/月）、オーバースペック

### 4. 認証: Streamlit Session State + 環境変数

**決定**: 環境変数にパスワードを保存、Streamlit Session Stateで認証状態管理

**実装**:
```python
import streamlit as st
import os

def check_authentication():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 ログイン")
        password = st.text_input("パスワードを入力してください", type="password")

        if st.button("ログイン"):
            if password == os.getenv("APP_PASSWORD"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("パスワードが間違っています")
        st.stop()

# メイン処理
check_authentication()
st.title("競馬解析アプリ")
# ... 以降のアプリロジック
```

**理由**:
- 最もシンプル
- 1日限定使用には十分
- AWS Secrets Managerは追加コスト（$0.40/月）がかかる
- Session Stateでブラウザごとに認証状態を保持

### 5. デプロイ: AWS App Runner

**決定**: Dockerコンテナ化してAWS App Runnerにデプロイ

**構成**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**環境変数**:
- `OPENAI_API_KEY`: GPT-5 APIキー
- `APP_PASSWORD`: アプリパスワード
- `AWS_REGION`: DynamoDBリージョン
- `DYNAMODB_TABLE`: テーブル名

**理由**:
- コンテナから直接デプロイ可能（GitHubやECR連携）
- オートスケーリング（ただし今回は最小構成: 0.25vCPU, 0.5GB）
- HTTPS自動対応
- 1日使用なら$0.50-1.00程度
- 設定が簡単（ECSより遥かにシンプル）

**代替案**:
- EC2 t3.micro: 無料枠使えるが、セットアップが面倒、管理が必要
- Lambda + API Gateway: Streamlitには不向き（WebSocket必要）
- ECS Fargate: 設定が複雑、コストも高め

**コスト詳細**:
- App Runner基本料金: $0.007/hour × 24時間 = $0.168/日
- vCPU (0.25): $0.032/hour × 実行時間
- メモリ (0.5GB): $0.0035/hour × 実行時間
- **1日使用（数時間稼働）**: 約$0.50-1.00

### 6. LLM統合: OpenAI Python SDK (GPT-5)

**決定**: openai Python SDKを使用してGPT-5と連携

**実装パターン**:
```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_horses(race_data, custom_prompt=""):
    """
    競馬データを解析してGPT-5から結果を取得

    Args:
        race_data: dict - スクレイピングしたレースデータ
        custom_prompt: str - ユーザー定義のカスタムプロンプト

    Returns:
        dict - 解析結果 (individual, comparison, ranking)
    """

    # システムプロンプト
    system_prompt = """
あなたは競馬データ解析の専門家です。
提供されたデータに基づいて、各馬の強み・弱点を客観的に分析してください。
以下の観点から分析してください：
- 過去の成績（着順、タイム）
- レース距離との相性
- 前走からの期間
- 騎手・調教師の実績
- 親馬の実績

分析は具体的なデータに基づき、明確な根拠を示してください。
"""

    # データを構造化して送信
    user_prompt = f"""
# レース情報
- 距離: {race_data['distance']}
- 馬場: {race_data['track_type']}

# 出走馬データ
{format_race_data(race_data)}

# カスタム指示
{custom_prompt if custom_prompt else "標準的な解析を行ってください"}

# 出力形式
以下の3つの観点で分析結果を提供してください：

## 1. 個別馬分析
各馬について、強み・弱点をリスト形式で記載

## 2. 馬同士の比較
注目すべき馬同士の比較分析

## 3. おすすめランキング
上位5頭を推奨順にランキング
"""

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=4000
    )

    return parse_gpt_response(response.choices[0].message.content)

def format_race_data(race_data):
    """データを読みやすい形式に整形"""
    output = []
    for horse in race_data['horses']:
        output.append(f"""
馬名: {horse['name']}
- 過去5走: {horse['recent_results']}
- 前走からの期間: {horse['days_since_last_race']}日
- 騎手: {horse['jockey_name']} (勝率: {horse['jockey_win_rate']}%)
- 父馬: {horse['sire_name']} (賞金: {horse['sire_earnings']})
- 母馬: {horse['dam_name']} (賞金: {horse['dam_earnings']})
""")
    return "\n".join(output)
```

**プロンプト戦略**:
- システムプロンプト: 競馬解析専門家としてのペルソナ設定
- ユーザープロンプト: 構造化データ + カスタムプロンプト
- 出力形式を明示的に指定（個別分析、比較、ランキング）

**コスト最適化**:
- 不要なデータは送信しない（トークン数削減）
- キャッシュを活用（同じレースの再解析を避ける）

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User (Mobile)                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   AWS App Runner                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Streamlit Application                       │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  UI Layer (Streamlit Components)                │  │  │
│  │  │  - Date/Track/Race selector (Dropdown)          │  │  │
│  │  │  - Custom prompt input                          │  │  │
│  │  │  - Results display (3 tabs)                     │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Auth Module                                    │  │  │
│  │  │  - Session state management                     │  │  │
│  │  │  - Password verification                        │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Scraper Module (requests + BeautifulSoup)     │  │  │
│  │  │  - NetkeibaScraper class                       │  │  │
│  │  │  - Race/Horse/Jockey scrapers                  │  │  │
│  │  │  - Error handling & retry logic                │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Cache Module                                   │  │  │
│  │  │  - DynamoDB client                              │  │  │
│  │  │  - Get/Set with TTL                             │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Analyzer Module                                │  │  │
│  │  │  - OpenAI GPT-5 integration                     │  │  │
│  │  │  - Prompt engineering                           │  │  │
│  │  │  - Response parsing                             │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌─────────────┐   ┌──────────────────┐   ┌──────────────┐
│  netkeiba   │   │  OpenAI API      │   │  DynamoDB    │
│  (scrape)   │   │   (GPT-5)        │   │  (Cache)     │
└─────────────┘   └──────────────────┘   └──────────────┘
```

## Data Flow

### レース解析フロー

```
1. ユーザー入力
   ↓
   日付、競馬場、レース番号を選択
   オプション: カスタムプロンプト入力
   ↓
2. レースID取得
   ↓
   DynamoDB キャッシュチェック (PK: RACE#{date}#{track}, SK: IDS)
   ├─ キャッシュヒット → レースID取得
   └─ キャッシュミス → netkeiba スクレイピング → DynamoDB保存
   ↓
3. レース詳細取得
   ↓
   DynamoDB キャッシュチェック (PK: RACE#{race_id}, SK: METADATA)
   ├─ キャッシュヒット → 出走馬リスト取得
   └─ キャッシュミス → netkeiba スクレイピング → DynamoDB保存
   ↓
4. 各馬の詳細データ取得（並列処理可能）
   ↓
   for each horse:
     ├─ 馬情報 (PK: HORSE#{horse_id}, SK: RESULTS)
     ├─ 親馬情報 (PK: HORSE#{horse_id}, SK: PARENT)
     └─ 騎手情報 (PK: JOCKEY#{jockey_id}, SK: STATS)

   各データについてキャッシュチェック
   ├─ キャッシュヒット → 使用
   └─ キャッシュミス → スクレイピング → DynamoDB保存
   ↓
5. データ統合
   ↓
   全データを1つの構造化オブジェクトに統合
   ↓
6. GPT-5解析
   ↓
   構造化データ + カスタムプロンプトをGPT-5に送信
   ↓
   解析結果取得:
   - 個別馬分析
   - 馬同士の比較
   - おすすめランキング
   ↓
7. 結果表示
   ↓
   Streamlit 3タブで表示:
   - タブ1: 個別馬分析
   - タブ2: 馬同士の比較
   - タブ3: おすすめランキング
```

## Module Structure

```
keiba_kaisetsu/
├── app.py                     # Streamlitメインアプリ
├── requirements.txt           # Python依存関係
├── Dockerfile                 # コンテナ定義
├── .env.example               # 環境変数テンプレート
├── README.md                  # ドキュメント
├── scraper/
│   ├── __init__.py
│   ├── base.py                # BaseScraper (共通処理)
│   ├── race.py                # RaceScraper
│   ├── horse.py               # HorseScraper
│   └── jockey.py              # JockeyScraper
├── analyzer/
│   ├── __init__.py
│   ├── gpt_analyzer.py        # GPT-5統合
│   └── prompts.py             # プロンプトテンプレート
├── cache/
│   ├── __init__.py
│   └── dynamodb.py            # DynamoDBクライアント
└── utils/
    ├── __init__.py
    ├── parser.py              # HTMLパース補助
    └── formatter.py           # データ整形
```

## Risks / Trade-offs

### リスク 1: netkeibaのHTML構造変更

**リスク**: スクレイピング対象のHTML構造が変わると動作しなくなる

**影響度**: 高

**軽減策**:
- CSSセレクタを複数パターン用意（フォールバック）
- クラス名だけでなく、構造的特徴も使う
- エラーハンドリングを充実
- 定期的な動作確認（1日使用なので手動確認で十分）

**リカバリープラン**:
- エラー時は詳細ログを出力
- 取得できた部分データのみで解析を試みる

### リスク 2: スクレイピング頻度制限

**リスク**: 頻繁なアクセスでIPブロックされる可能性

**影響度**: 中

**軽減策**:
- リクエスト間に1秒の待機時間
- User-Agent設定
- DynamoDBキャッシュで重複リクエスト削減（7日間保持）
- 1日30アクセス程度なので問題になる可能性は低い

### リスク 3: GPT-5 APIコスト超過

**リスク**: 大量データ送信でAPIコストが想定以上になる

**影響度**: 中

**軽減策**:
- データを要約してから送信（不要な情報は削除）
- トークン数を計算してログ出力
- 1レースあたりの最大トークン数を制限
- キャッシュを積極活用

**想定コスト**:
- 1レースあたり: 約3,000-5,000トークン（入力）
- 30アクセス × 平均4,000トークン = 120,000トークン
- GPT-5料金（想定）: 入力$0.01/1Kトークン → 約$1.20/日

### リスク 4: 文字化け

**リスク**: エンコーディング処理が不適切だと文字化けする

**影響度**: 中

**軽減策**:
- `response.apparent_encoding` で自動検出
- フォールバックとして `euc-jp`, `shift_jis`, `utf-8` を順に試行
- テスト時に日本語データを確認

### リスク 5: DynamoDBのデータサイズ制限

**リスク**: 1アイテムのサイズ制限（400KB）を超える可能性

**影響度**: 低

**軽減策**:
- データを分割して保存（馬ごと、レース結果ごと）
- 不要なデータは保存しない
- 調査結果から見て、1馬のデータは20-30KB程度なので問題なし

## Performance Considerations

### レスポンス時間目標

| シナリオ | 目標時間 | 備考 |
|---------|---------|------|
| 初回アクセス（キャッシュなし） | 60秒以内 | スクレイピング30-60秒 + GPT-5解析10-30秒 |
| 2回目以降（キャッシュあり） | 30秒以内 | GPT-5解析のみ |
| 同一レース再解析 | 10秒以内 | 全キャッシュヒット |

### スケーラビリティ

- **現在の想定**: 1日30アクセス
- **対応可能**: 1日100アクセス程度まではコード変更なしで対応可能
- **ボトルネック**: スクレイピング速度（並列化で改善可能）

## Security Considerations

### 1. 認証
- 簡易パスワード認証（環境変数）
- Session Stateでセッション管理
- ブラウザリロードで認証解除

### 2. API Key管理
- 環境変数で管理（コードに含めない）
- App Runnerの環境変数機能を使用
- `.env`ファイルは`.gitignore`に追加

### 3. データセキュリティ
- DynamoDB: IAMロールでアクセス制御
- App Runner: VPC不要（パブリックアクセスのみ）
- HTTPS: App Runnerが自動提供

### 4. スクレイピング
- robots.txt確認（netkeiba）
- 適切な待機時間（1秒/リクエスト）
- User-Agent明示

## Monitoring & Logging

### アプリケーションログ
- Streamlitの標準ログ出力
- スクレイピングエラー: 詳細ログ出力
- GPT-5リクエスト: トークン数ログ

### AWSログ
- CloudWatch Logs: App Runnerの標準出力
- DynamoDB: アクセスログ（必要に応じて）

### エラー通知
- 初期は手動確認（1日使用のため）
- 将来的にはSNS連携を検討

## Testing Strategy

### 単体テスト
- スクレイパー: 各ページパース処理
- キャッシュ: DynamoDB読み書き
- GPT-5統合: モックを使用

### 統合テスト
- エンドツーエンド: 実際のURLでスクレイピング
- キャッシュフロー: キャッシュヒット/ミス

### 手動テスト
- UI/UX: スマホでの操作確認
- エラーハンドリング: 異常系の動作確認

## Deployment Plan

### 1. ローカル開発
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### 2. Dockerビルド
```bash
docker build -t keiba-app .
docker run -p 8501:8501 --env-file .env keiba-app
```

### 3. AWS App Runnerデプロイ
1. ECRにイメージをプッシュ
2. App Runnerサービス作成
3. 環境変数設定
4. デプロイ実行

### 4. DynamoDB設定
- テーブル作成（オンデマンドモード）
- TTL有効化（`ttl`属性）

## Open Questions

- [ ] GPT-5のトークン制限・料金体系は? → 実装時に最新情報を確認
- [ ] netkeibaのスクレイピング規約は? → robots.txt確認
- [ ] App Runnerの最小構成でパフォーマンスは十分か? → 0.25vCPU/0.5GBから開始、必要に応じて増強
- [ ] キャッシュ期間7日は適切か? → 運用しながら調整

---

**設計完了日**: 2025-10-18
**スクレイピング調査**: [USER/SCRAPING_INVESTIGATION_REPORT.md](../../../USER/SCRAPING_INVESTIGATION_REPORT.md)
