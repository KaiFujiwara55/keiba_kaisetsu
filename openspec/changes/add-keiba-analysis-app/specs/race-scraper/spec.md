# Race Scraper Specification

## ADDED Requirements

### Requirement: netkeiba Race Data Scraping

The system SHALL scrape race-related data from netkeiba.com using requests and BeautifulSoup4, without requiring JavaScript rendering engines like Selenium.

#### Scenario: Fetch available races by date

- **WHEN** user provides a race date (YYYYMMDD format)
- **THEN** the system fetches the race list page from `https://race.netkeiba.com/top/?kaisai_date={date}`
- **AND** extracts all race_ids with their associated track names and race numbers
- **AND** returns a structured list of available races: `{track_name, race_number, race_id}`

#### Scenario: Select race by track and race number

- **WHEN** user selects a specific track name and race number from the available races
- **THEN** the system identifies the corresponding race_id from the fetched data
- **AND** returns the correct race_id for further processing

#### Scenario: Fetch race details

- **WHEN** the system has determined a race_id
- **THEN** the system fetches race details from `https://race.netkeiba.com/race/shutuba.html?race_id={race_id}`
- **AND** extracts the following information:
  - Race distance (meters)
  - Track type (turf/dirt/障害)
  - List of horses with:
    - Horse name
    - Horse ID
    - Gate number (馬番)
    - Frame number (枠)
    - Weight carried (斤量)
    - Jockey name
    - Jockey ID
- **AND** returns structured race data

#### Scenario: Handle encoding correctly

- **WHEN** fetching any netkeiba page
- **THEN** the system automatically detects character encoding (typically EUC-JP)
- **AND** correctly decodes Japanese text without mojibake (文字化け)

### Requirement: Request Rate Limiting

The system SHALL implement appropriate rate limiting to avoid overloading netkeiba servers.

#### Scenario: Delay between requests

- **WHEN** making multiple requests to netkeiba
- **THEN** the system waits at least 1 second between consecutive requests
- **AND** logs each request URL and timestamp

### Requirement: Error Handling

The system SHALL handle scraping errors gracefully and provide meaningful error messages.

#### Scenario: HTTP error handling

- **WHEN** a request returns a non-200 status code
- **THEN** the system logs the error with URL and status code
- **AND** raises a custom ScrapingError exception
- **AND** provides retry logic up to 3 attempts with exponential backoff

#### Scenario: Parsing error handling

- **WHEN** HTML structure doesn't match expected patterns
- **THEN** the system logs a warning with details
- **AND** attempts alternative CSS selectors
- **AND** returns partial data if available
- **AND** raises an error only if no data can be extracted

### Requirement: User-Agent Configuration

The system SHALL set an appropriate User-Agent header to identify the scraper.

#### Scenario: Set User-Agent header

- **WHEN** making any HTTP request to netkeiba
- **THEN** the system includes a User-Agent header mimicking a standard browser
- **AND** uses a consistent User-Agent across all requests
