# Web Interface Specification

## ADDED Requirements

### Requirement: Streamlit-based Mobile-Friendly UI

The system SHALL provide a Streamlit web interface optimized for mobile device usage.

#### Scenario: User authentication

- **WHEN** user first accesses the application
- **THEN** the system displays a login screen with password input field
- **AND** validates entered password against environment variable `APP_PASSWORD`
- **AND** stores authentication state in Streamlit session state
- **AND** displays error message for incorrect password
- **AND** redirects to main interface upon successful authentication

#### Scenario: Race selection via dropdowns

- **WHEN** authenticated user accesses the main interface
- **THEN** the system displays three dropdown selectors in order:
  1. Race date selector (date picker or text input in YYYYMMDD format)
  2. Track name selector (populated after date is selected)
  3. Race number selector (populated after track is selected)
- **AND** dynamically populates track names and race numbers based on previous selections
- **AND** displays loading spinner while fetching available races

#### Scenario: Custom prompt input

- **WHEN** user has selected a race
- **THEN** the system displays an optional text area for custom analysis prompts
- **AND** provides placeholder text with example custom prompts
- **AND** allows user to leave the field empty for standard analysis

#### Scenario: Trigger analysis

- **WHEN** user clicks "解析開始" (Start Analysis) button
- **THEN** the system validates that all required selections are made
- **AND** displays a progress indicator showing:
  - "データ取得中..." (Fetching data)
  - "LLM解析中..." (Analyzing with LLM)
- **AND** estimated time remaining

### Requirement: Analysis Results Display

The system SHALL display analysis results in three separate tabs.

#### Scenario: Display individual horse analysis

- **WHEN** analysis is complete
- **THEN** the system displays results in a tabbed interface
- **AND** Tab 1 "個別馬分析" shows:
  - Each horse's name
  - Strengths (bullet list)
  - Weaknesses (bullet list)
  - Formatted in expandable sections for mobile readability

#### Scenario: Display comparison analysis

- **WHEN** user switches to Tab 2 "馬同士の比較"
- **THEN** the system displays head-to-head comparisons
- **AND** uses collapsible sections for each comparison
- **AND** highlights key differences with visual formatting

#### Scenario: Display recommendation ranking

- **WHEN** user switches to Tab 3 "おすすめランキング"
- **THEN** the system displays top 5 recommended horses
- **AND** shows ranking in numbered list format (1位 to 5位)
- **AND** includes reasoning for each ranking
- **AND** displays confidence indicators if available

### Requirement: Mobile Responsiveness

The system SHALL ensure usability on mobile devices.

#### Scenario: Responsive layout

- **WHEN** accessed from a mobile device
- **THEN** the system adjusts layout to fit small screens
- **AND** uses full-width components
- **AND** ensures text is readable without horizontal scrolling
- **AND** touch targets are appropriately sized for finger input

### Requirement: Error Display

The system SHALL display user-friendly error messages.

#### Scenario: Scraping error

- **WHEN** data scraping fails
- **THEN** the system displays an error message explaining the issue
- **AND** suggests potential solutions (e.g., "レースが見つかりませんでした。日付を確認してください")
- **AND** allows user to retry with different inputs

#### Scenario: LLM error

- **WHEN** GPT-5 analysis fails
- **THEN** the system displays a message explaining the API error
- **AND** provides option to retry analysis
- **AND** optionally displays partial results if available
