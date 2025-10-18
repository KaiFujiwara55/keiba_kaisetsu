# Horse Scraper Specification

## ADDED Requirements

### Requirement: Horse Performance Data Scraping

The system SHALL scrape individual horse data from netkeiba.com horse detail pages.

#### Scenario: Fetch horse past performance

- **WHEN** given a horse_id
- **THEN** the system fetches horse details from `https://db.netkeiba.com/horse/{horse_id}`
- **AND** extracts the following information:
  - Past race results (all races):
    - Race date
    - Track name
    - Race name
    - Finishing position (着順)
    - Race time
    - Race distance
  - Days since last race (calculated from current date and most recent race date)
- **AND** returns structured horse performance data

#### Scenario: Fetch parent horse information

- **WHEN** given a horse_id
- **THEN** the system fetches horse pedigree information
- **AND** extracts parent (sire and dam) horse IDs
- **AND** for each parent, fetches:
  - Parent horse name
  - Total earnings (獲得賞金)
  - Career record (1st, 2nd, 3rd place counts)
- **AND** returns structured parent horse data

### Requirement: Data Extraction Accuracy

The system SHALL accurately parse HTML tables containing race results.

#### Scenario: Parse race result table

- **WHEN** parsing a horse detail page
- **THEN** the system identifies the race results table by header content
- **AND** correctly maps table columns to data fields
- **AND** handles missing or null values gracefully
- **AND** returns empty fields for data that cannot be found

### Requirement: Performance Optimization

The system SHALL minimize redundant requests for parent horse data.

#### Scenario: Check cache before fetching parent data

- **WHEN** fetching parent horse information
- **THEN** the system first checks DynamoDB cache for existing parent data
- **AND** only makes HTTP requests for cache misses
- **AND** stores fetched parent data in cache with 7-day TTL
