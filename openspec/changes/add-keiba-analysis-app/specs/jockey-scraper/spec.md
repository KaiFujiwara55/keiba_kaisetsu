# Jockey Scraper Specification

## ADDED Requirements

### Requirement: Jockey Performance Data Scraping

The system SHALL scrape jockey performance statistics from netkeiba.com jockey detail pages.

#### Scenario: Fetch jockey statistics

- **WHEN** given a jockey_id
- **THEN** the system fetches jockey details from `https://db.netkeiba.com/jockey/{jockey_id}`
- **AND** extracts the following information:
  - Recent 5-year performance statistics:
    - Win rate (勝率)
    - Place rate (複勝率)
    - Total races
    - 1st, 2nd, 3rd place counts
  - Basic information:
    - Jockey name
    - Debut year
    - Height/weight
- **AND** returns structured jockey performance data

#### Scenario: Parse statistics table

- **WHEN** parsing jockey statistics
- **THEN** the system identifies the statistics table by header content (looking for "勝率", "複勝率")
- **AND** extracts the most recent 5 years of data
- **AND** calculates average win rate and place rate across the 5-year period
- **AND** handles cases where less than 5 years of data is available

### Requirement: Data Validation

The system SHALL validate extracted jockey statistics.

#### Scenario: Validate percentage values

- **WHEN** extracting win rate or place rate
- **THEN** the system validates that values are between 0 and 100
- **AND** converts percentage strings to float numbers
- **AND** logs a warning if values are out of expected range
- **AND** returns null for invalid values
