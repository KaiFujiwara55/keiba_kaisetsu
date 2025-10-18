# GPT-5 API トークン制限・使用量調査レポート

**調査日**: 2025-10-18
**目的**: GPT-5 APIのトークン制限、使用量カウント方法、コスト最適化戦略を明確化

---

## 🎯 調査結果サマリー

### トークン制限
- **入力上限**: 272,000 トークン
- **出力上限**: 128,000 トークン
- **合計コンテキストウィンドウ**: 400,000 トークン

### 料金体系（2025年）
- **入力**: $1.25 / 1M トークン
- **出力**: $10.00 / 1M トークン
- **キャッシュ入力**: $0.125 / 1M トークン（90%割引）

### ⚠️ 重要な発見: Reasoning Tokens
GPT-5は**推論トークン**（reasoning tokens）を内部で生成し、これが**出力トークンとして課金**される。

---

## 📊 詳細調査結果

### 1. トークン制限

#### API制限（実測値）
```
入力トークン上限: 272,000 トークン
出力トークン上限: 128,000 トークン
合計: 400,000 トークン
```

#### 実装時の注意点
- ドキュメントには400,000トークンと記載されているが、実際は入力272,000 + 出力128,000に分かれている
- 入力が272,000トークンを超えるとエラー: `"Input tokens exceed the configured limit of 272,000 tokens"`

### 2. トークン使用量のカウント方法

#### API レスポンスの `usage` オブジェクト

すべてのOpenAI APIレスポンスには `usage` キーが含まれ、以下の情報が取得できる:

```python
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1677858242,
  "model": "gpt-5",
  "usage": {
    "prompt_tokens": 13,        # 入力トークン数
    "completion_tokens": 7,     # 出力トークン数（推論トークン含む）
    "total_tokens": 20,         # 合計
    "reasoning_tokens": 1344    # 推論トークン数（GPT-5のみ）
  },
  "choices": [...]
}
```

#### トークンの種類

| トークンタイプ | 説明 | 課金対象 |
|---------------|------|---------|
| `prompt_tokens` | ユーザーが送信した入力トークン | ✅ 入力料金 |
| `completion_tokens` | モデルが生成した出力トークン | ✅ 出力料金 |
| `reasoning_tokens` | 内部推論トークン（GPT-5のみ） | ✅ 出力料金に含まれる |
| `cached_tokens` | キャッシュされた入力トークン | ✅ キャッシュ料金（90%割引） |

#### ストリーミングモードでの使用量取得

ストリーミングモードを使用する場合、使用量データにアクセスするには以下のパラメータが必要:

```python
response = client.chat.completions.create(
    model="gpt-5",
    messages=[...],
    stream=True,
    stream_options={"include_usage": true}  # ← 重要!
)
```

### 3. GPT-5のReasoning Tokens（推論トークン）

#### 推論トークンとは？

GPT-5は複雑なタスクに対して、内部的に「考える」ステップを生成する。これが**reasoning tokens**として記録される。

**重要**: 推論トークンは**出力トークンとして課金される**

#### 実例

```
タスク: 5,000トークンのコーディング問題

最小推論設定（reasoning_effort: "minimal"）:
- 入力: 5,000 トークン
- 出力: 2,000 トークン
- コスト: (5000 × $1.25 + 2000 × $10) / 1,000,000 = $0.026

高推論設定（reasoning_effort: "high"）:
- 入力: 5,000 トークン
- 推論: 10,000 トークン（見えない）
- 出力: 2,000 トークン
- 合計出力: 12,000 トークン
- コスト: (5000 × $1.25 + 12000 × $10) / 1,000,000 = $0.126

→ 約5倍のコスト増加！
```

#### 競馬解析での影響

競馬データ解析は複雑なタスクなので、GPT-5が多くの推論トークンを使う可能性が高い。

**推定**:
- 1レースあたり入力: 4,000 トークン
- 1レースあたり出力: 2,000 トークン（表示）
- 1レースあたり推論: 3,000-5,000 トークン（非表示）
- **実質出力**: 5,000-7,000 トークン

### 4. 料金体系（2025年）

#### GPT-5 モデルバリエーション

| モデル | 入力料金 | 出力料金 | キャッシュ入力料金 |
|--------|---------|---------|------------------|
| GPT-5 | $1.25 / 1M | $10.00 / 1M | $0.125 / 1M |
| GPT-5-mini | $0.25 / 1M | $2.00 / 1M | $0.025 / 1M |
| GPT-5-nano | $0.05 / 1M | $0.40 / 1M | $0.005 / 1M |

#### キャッシング機能（90%割引）

OpenAIのセマンティックキャッシュシステムを使うと、繰り返し使用される入力トークンが**90%割引**になる。

**例**:
- 通常入力: $1.25 / 1M トークン
- キャッシュ入力: $0.125 / 1M トークン

### 5. コスト見積もり（競馬解析アプリ）

#### 1レースあたりのコスト（推論トークン含む）

**シナリオ1: キャッシュなし**
```
入力: 4,000 トークン × $1.25 / 1M = $0.005
出力: 7,000 トークン × $10 / 1M = $0.070
合計: $0.075 / レース
```

**シナリオ2: キャッシュあり（馬・騎手データ再利用）**
```
新規入力: 1,000 トークン × $1.25 / 1M = $0.00125
キャッシュ入力: 3,000 トークン × $0.125 / 1M = $0.000375
出力: 7,000 トークン × $10 / 1M = $0.070
合計: $0.072 / レース（約4%削減）
```

#### 30レース（1日使用）の合計コスト

- **キャッシュなし**: 30 × $0.075 = **$2.25**
- **キャッシュあり**: 30 × $0.072 = **$2.16**

#### 推論トークンを制御する方法

GPT-5では `reasoning_effort` パラメータで推論量を調整可能:

```python
response = client.chat.completions.create(
    model="gpt-5",
    messages=[...],
    reasoning_effort="minimal"  # "minimal", "medium", "high"
)
```

- `minimal`: 最小限の推論（高速、低コスト）
- `medium`: 標準的な推論（デフォルト）
- `high`: 最大限の推論（高品質、高コスト）

**推奨**: 競馬解析では`medium`または`minimal`を使用してコスト削減

---

## 🛠️ 実装推奨事項

### 1. トークン制限の設定

```python
# 安全マージンを含めた制限
MAX_INPUT_TOKENS = 250000  # 272,000の約92%
MAX_OUTPUT_TOKENS = 100000  # 128,000の約78%
RECOMMENDED_MAX_OUTPUT = 8000  # 実用的な上限
```

### 2. 使用量ロギング

```python
def analyze_horses(race_data, custom_prompt=""):
    response = client.chat.completions.create(
        model="gpt-5",
        messages=[...],
        reasoning_effort="medium",  # コスト制御
        max_tokens=8000
    )

    # 使用量ログ
    usage = response.usage
    logger.info(f"Token usage: "
                f"input={usage.prompt_tokens}, "
                f"output={usage.completion_tokens}, "
                f"reasoning={usage.get('reasoning_tokens', 0)}, "
                f"total={usage.total_tokens}")

    # コスト計算
    input_cost = usage.prompt_tokens * 1.25 / 1_000_000
    output_cost = usage.completion_tokens * 10.0 / 1_000_000
    total_cost = input_cost + output_cost

    logger.info(f"Estimated cost: ${total_cost:.4f}")

    return parse_response(response)
```

### 3. 事前トークンカウント

送信前にトークン数を推定:

```python
import tiktoken

def count_tokens(text, model="gpt-5"):
    """テキストのトークン数をカウント"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# 使用例
prompt_text = format_race_data(race_data)
token_count = count_tokens(prompt_text)

if token_count > MAX_INPUT_TOKENS:
    # データを削減
    logger.warning(f"Input too large: {token_count} tokens, reducing...")
    prompt_text = reduce_data(race_data, target_tokens=MAX_INPUT_TOKENS)
```

### 4. データ削減の優先順位

トークン超過時の削減順序:

1. 過去レース結果を10→5→3レースに削減
2. 親馬の詳細統計を除外
3. 騎手情報を要約（5年→3年）
4. レース距離・タイムの詳細を丸める

### 5. ストリーミング対応（オプション）

ユーザーエクスペリエンス向上のため:

```python
response = client.chat.completions.create(
    model="gpt-5",
    messages=[...],
    stream=True,
    stream_options={"include_usage": True}
)

for chunk in response:
    if chunk.choices[0].delta.content:
        # リアルタイム表示
        print(chunk.choices[0].delta.content, end="")

    # 最後のチャンクに使用量情報
    if hasattr(chunk, 'usage') and chunk.usage:
        logger.info(f"Final usage: {chunk.usage}")
```

---

## 📋 仕様への追加推奨事項

### 追加すべきRequirement

```markdown
### Requirement: Token Limit Compliance

The system SHALL respect GPT-5 API token limits and monitor usage.

#### Scenario: Enforce input token limit

- **WHEN** preparing data for GPT-5
- **THEN** the system counts tokens using tiktoken library
- **AND** if estimated input tokens exceed 250,000
- **THEN** the system reduces data in priority order:
  1. Limit past races to 5 most recent
  2. Exclude parent horse detailed career stats
  3. Summarize jockey information to 3-year stats
- **AND** logs a warning about data reduction

#### Scenario: Set output token limit

- **WHEN** making GPT-5 API request
- **THEN** the system sets max_tokens parameter to 8,000
- **AND** sets reasoning_effort to "medium" for cost optimization

#### Scenario: Log token usage and cost

- **WHEN** GPT-5 API response is received
- **THEN** the system extracts usage object from response
- **AND** logs the following metrics:
  - prompt_tokens (input)
  - completion_tokens (output)
  - reasoning_tokens (if available)
  - total_tokens
- **AND** calculates and logs estimated cost:
  - Input cost: prompt_tokens × $1.25 / 1M
  - Output cost: completion_tokens × $10.00 / 1M
- **AND** stores usage metrics for monitoring
```

---

## 🎯 まとめ

### 重要ポイント

1. **トークン制限**: 入力272K、出力128K（合計400K）
2. **推論トークン**: GPT-5は非表示の推論トークンを生成し、出力として課金される
3. **使用量取得**: `response.usage` オブジェクトから正確なトークン数を取得可能
4. **コスト**: 1レースあたり約$0.07-0.08（推論トークン含む）
5. **最適化**: `reasoning_effort="medium"` と `max_tokens=8000` で制御

### 次のアクション

- [ ] llm-analyzer/spec.md にトークン制限要件を追加
- [ ] design.md のコスト見積もりを更新（推論トークン考慮）
- [ ] 実装時に tiktoken ライブラリを使用してトークンカウント
- [ ] ログに使用量とコストを記録

---

**調査完了日**: 2025-10-18
**参考**: OpenAI公式ドキュメント、コミュニティフォーラム
