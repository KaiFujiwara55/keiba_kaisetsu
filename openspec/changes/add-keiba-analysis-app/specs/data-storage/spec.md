# Data Storage Specification

## ADDED Requirements

### Requirement: DynamoDB Caching Layer

The system SHALL use AWS DynamoDB to cache scraped data with automatic expiration.

#### Scenario: Store race data with TTL

- **WHEN** race data is successfully scraped
- **THEN** the system stores the data in DynamoDB with:
  - PK: `RACE#{race_id}`
  - SK: `METADATA`
  - data: complete race information including horse list
  - fetched_at: Unix timestamp
  - ttl: Unix timestamp for 7 days in the future
- **AND** overwrites any existing entry with the same PK/SK

#### Scenario: Store horse data with TTL

- **WHEN** horse performance data is successfully scraped
- **THEN** the system stores two items:
  1. Horse results:
     - PK: `HORSE#{horse_id}`
     - SK: `RESULTS`
     - data: past race results
     - ttl: 7 days
  2. Parent horse data:
     - PK: `HORSE#{horse_id}`
     - SK: `PARENT`
     - data: sire and dam information
     - ttl: 7 days

#### Scenario: Store jockey data with TTL

- **WHEN** jockey statistics are successfully scraped
- **THEN** the system stores in DynamoDB with:
  - PK: `JOCKEY#{jockey_id}`
  - SK: `STATS`
  - data: win rate, place rate, and other statistics
  - ttl: 7 days

#### Scenario: Store available races by date

- **WHEN** the system fetches available races for a specific date
- **THEN** the system stores in DynamoDB with:
  - PK: `DATE#{YYYYMMDD}`
  - SK: `RACES`
  - data: list of {track_name, race_number, race_id}
  - ttl: 1 day (shorter TTL since race schedules change)

### Requirement: Cache Retrieval

The system SHALL check cache before making HTTP requests to netkeiba.

#### Scenario: Check cache before scraping

- **WHEN** the system needs any data (race, horse, jockey)
- **THEN** the system first queries DynamoDB with the appropriate PK/SK
- **AND** if item exists and TTL has not expired:
  - Returns cached data immediately
  - Logs cache hit
- **AND** if item does not exist or TTL expired:
  - Proceeds with scraping
  - Logs cache miss

### Requirement: Single Table Design

The system SHALL use a single DynamoDB table for all data types.

#### Scenario: Table structure

- **WHEN** the DynamoDB table is created
- **THEN** the table has the following schema:
  - Table name: `keiba_data` (configurable via environment variable)
  - Primary key: PK (String)
  - Sort key: SK (String)
  - Billing mode: On-demand (pay per request)
  - TTL attribute: `ttl` (enabled)

### Requirement: Error Handling

The system SHALL handle DynamoDB errors gracefully.

#### Scenario: Handle DynamoDB unavailability

- **WHEN** DynamoDB request fails due to network or service error
- **THEN** the system logs the error
- **AND** continues with scraping (treats as cache miss)
- **AND** does not fail the entire request

#### Scenario: Handle item size limits

- **WHEN** storing data larger than 400KB (DynamoDB item limit)
- **THEN** the system logs a warning
- **AND** splits the data into multiple items if possible
- **AND** falls back to skipping cache for oversized items
