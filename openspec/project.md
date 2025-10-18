# Project Context

## Purpose

競馬レース解析アプリケーション - netkeibaから取得した競馬データをGPT-5で解析し、各馬の強み・弱点、比較分析、おすすめランキングを提供するWebアプリ。

## Tech Stack

### Backend
- Python 3.11+
- Streamlit (Webフレームワーク)
- requests + BeautifulSoup4 (スクレイピング)
- boto3 (AWS SDK)
- OpenAI Python SDK (GPT-5統合)

### Infrastructure
- AWS App Runner (コンテナホスティング)
- AWS DynamoDB (NoSQLデータベース、キャッシュ)
- Docker (コンテナ化)

### External APIs
- OpenAI GPT-5 API
- netkeiba.com (スクレイピング対象)

## Project Conventions

### Code Style
- PEP 8準拠
- Type hints使用（Python 3.11+）
- Docstrings: Google形式
- 変数名: snake_case
- クラス名: PascalCase
- 定数: UPPER_SNAKE_CASE

### Architecture Patterns
- モノリシックStreamlitアプリケーション
- モジュラー設計（scraper, analyzer, cache分離）
- Single Table Design (DynamoDB)
- キャッシュファースト戦略

### Testing Strategy
- Unit tests: pytest
- Integration tests: 実際のURL使用
- Manual testing: スマホでのE2Eテスト
- テストカバレッジ: 主要ロジック70%以上

### Git Workflow
- main branch: 本番環境
- feature branches: 機能開発
- Commit message: 日本語OK、簡潔に

## Domain Context

### 競馬データの構造
- **レース**: 日付、競馬場、レース番号で一意に識別
- **馬**: horse_idで識別、過去成績・親馬情報あり
- **騎手**: jockey_idで識別、勝率・複勝率などの統計あり

### スクレイピング対象
- netkeiba.com: 日本の競馬情報サイト
- 静的HTML（JavaScript不要）
- エンコーディング: EUC-JP
- レート制限: 1秒/リクエスト推奨

## Important Constraints

### 技術制約
- Selenium不使用（requestsのみ）
- DynamoDBアイテムサイズ制限: 400KB
- GPT-5トークン制限: 入力データ要約必須
- スマホ対応必須

### ビジネス制約
- 1日限定使用想定（30アクセス程度）
- 簡易パスワード認証のみ
- コスト最小化（1日$0.50-1.00目標）

### 法的/倫理的制約
- netkeibaの利用規約遵守
- robots.txt確認
- 適切なレート制限実施

## External Dependencies

### OpenAI API
- モデル: GPT-5
- 用途: 競馬データ解析
- 認証: API Key（環境変数）

### AWS Services
- App Runner: アプリホスティング
- DynamoDB: データキャッシュ（TTL: 7日）
- CloudWatch: ログ管理

### netkeiba.com
- スクレイピング対象
- robots.txt: 要確認
- レート制限: 1秒/リクエスト
