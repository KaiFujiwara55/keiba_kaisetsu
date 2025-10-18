# LLM Analyzer Specification

## ADDED Requirements

### Requirement: GPT-5 Integration for Horse Racing Analysis

The system SHALL integrate OpenAI GPT-5 to analyze horse racing data and provide insights.

#### Scenario: Analyze individual horses

- **WHEN** race data with all horses' information is provided
- **THEN** the system constructs a prompt with:
  - System role: "Expert horse racing data analyst"
  - Race metadata (distance, track type)
  - Each horse's past performance, jockey stats, parent horse data
  - User's custom prompt (if provided)
- **AND** sends the prompt to GPT-5 API
- **AND** receives analysis for each horse including:
  - Strengths (based on data)
  - Weaknesses (based on data)
  - Key factors to consider
- **AND** returns structured individual horse analysis

#### Scenario: Generate horse comparison analysis

- **WHEN** individual horse analyses are completed
- **THEN** the system requests GPT-5 to compare notable horses
- **AND** receives comparative analysis highlighting:
  - Head-to-head matchups
  - Relative advantages in the specific race conditions
  - Statistical comparisons
- **AND** returns structured comparison analysis

#### Scenario: Generate recommendation ranking

- **WHEN** all analyses are completed
- **THEN** the system requests GPT-5 to provide a top-5 recommendation ranking
- **AND** receives ranking with:
  - Ranked order (1st to 5th)
  - Reasoning for each placement based on data
  - Confidence level for each recommendation
- **AND** returns structured ranking data

#### Scenario: Handle custom user prompts

- **WHEN** user provides a custom analysis prompt
- **THEN** the system appends the custom prompt to the standard analysis request
- **AND** GPT-5 incorporates the custom instructions in its analysis
- **AND** returns analysis that addresses both standard and custom requirements

### Requirement: Token Limit Management

The system SHALL manage token limits through environment variable configuration and enforce constraints to prevent API errors.

#### Scenario: Load token limits from environment variables

- **WHEN** the analyzer module is initialized
- **THEN** the system reads the following environment variables:
  - `GPT5_MAX_INPUT_TOKENS` (default: 250000 if not set)
  - `GPT5_MAX_OUTPUT_TOKENS` (default: 8000 if not set)
  - `GPT5_REASONING_EFFORT` (default: "medium" if not set)
- **AND** validates that values are positive integers
- **AND** logs the configured token limits

#### Scenario: Enforce input token limit

- **WHEN** preparing data for GPT-5
- **THEN** the system counts tokens using tiktoken library
- **AND** if estimated input tokens exceed `GPT5_MAX_INPUT_TOKENS`
- **THEN** the system reduces data in priority order:
  1. Limit past races to 5 most recent (from 10)
  2. Exclude parent horse detailed career stats
  3. Summarize jockey information to 3-year stats (from 5)
  4. Round race times and distances to reduce precision
- **AND** logs a warning: "Input data reduced from X to Y tokens"
- **AND** recounts tokens after reduction

#### Scenario: Set output token limit

- **WHEN** making GPT-5 API request
- **THEN** the system sets `max_tokens` parameter to `GPT5_MAX_OUTPUT_TOKENS`
- **AND** sets `reasoning_effort` parameter to `GPT5_REASONING_EFFORT`
- **AND** logs the configured parameters

### Requirement: Token Usage Logging

The system SHALL log detailed token usage and cost information for every GPT-5 API call.

#### Scenario: Log token usage from API response

- **WHEN** GPT-5 API response is received successfully
- **THEN** the system extracts the `usage` object from response
- **AND** logs the following metrics:
  - `prompt_tokens` (input tokens)
  - `completion_tokens` (output tokens including reasoning)
  - `reasoning_tokens` (reasoning tokens if available)
  - `total_tokens` (total)
- **AND** calculates estimated cost:
  - Input cost: `prompt_tokens × $1.25 / 1,000,000`
  - Output cost: `completion_tokens × $10.00 / 1,000,000`
  - Total cost: sum of above
- **AND** logs in format: "GPT-5 usage: input=X, output=Y, reasoning=Z, total=T tokens, cost=$C"

#### Scenario: Estimate tokens before API call

- **WHEN** preparing data for GPT-5
- **THEN** the system counts tokens using tiktoken library
- **AND** logs estimated input token count
- **AND** compares with `GPT5_MAX_INPUT_TOKENS`

### Requirement: Token Optimization

The system SHALL optimize token usage to minimize API costs.

#### Scenario: Summarize data before sending

- **WHEN** preparing data for GPT-5
- **THEN** the system removes unnecessary fields and formatting
- **AND** summarizes redundant information
- **AND** limits past race results to the most recent 10 races per horse
- **AND** removes verbose descriptions and metadata

### Requirement: Error Handling

The system SHALL handle GPT-5 API errors gracefully.

#### Scenario: Handle API rate limits

- **WHEN** GPT-5 API returns a rate limit error
- **THEN** the system waits for the specified retry-after duration
- **AND** retries the request up to 3 times
- **AND** returns a user-friendly error message if all retries fail

#### Scenario: Handle API timeout

- **WHEN** GPT-5 API request times out
- **THEN** the system logs the timeout
- **AND** retries once with extended timeout
- **AND** returns a partial analysis or error message to the user

### Requirement: Response Parsing

The system SHALL parse GPT-5 responses into structured data.

#### Scenario: Parse markdown response

- **WHEN** GPT-5 returns analysis in markdown format
- **THEN** the system identifies section headers (e.g., "## 1. 個別馬分析")
- **AND** extracts content for each of the three analysis types
- **AND** returns a dictionary with keys: `individual`, `comparison`, `ranking`
- **AND** handles cases where GPT-5 deviates from expected format
