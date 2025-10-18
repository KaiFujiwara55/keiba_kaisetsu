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

### Requirement: Token Optimization

The system SHALL optimize token usage to minimize API costs.

#### Scenario: Summarize data before sending

- **WHEN** preparing data for GPT-5
- **THEN** the system removes unnecessary fields and formatting
- **AND** summarizes redundant information
- **AND** limits past race results to the most recent 10 races per horse
- **AND** logs the estimated token count before sending

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
