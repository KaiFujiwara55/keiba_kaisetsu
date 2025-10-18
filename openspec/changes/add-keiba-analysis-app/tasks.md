# Implementation Tasks

## 1. Project Setup
- [ ] 1.1 Create project directory structure
- [ ] 1.2 Initialize Git repository
- [ ] 1.3 Create virtual environment
- [ ] 1.4 Create requirements.txt with dependencies:
  - streamlit
  - requests
  - beautifulsoup4
  - boto3 (DynamoDB)
  - openai (GPT-5)
- [ ] 1.5 Create .env.example file with required environment variables
- [ ] 1.6 Create .gitignore file (include .env, __pycache__, venv/)

## 2. DynamoDB Setup
- [ ] 2.1 Create DynamoDB table `keiba_data` via AWS Console or CLI
- [ ] 2.2 Configure table with on-demand billing mode
- [ ] 2.3 Enable TTL on `ttl` attribute
- [ ] 2.4 Create IAM role for App Runner with DynamoDB access
- [ ] 2.5 Test DynamoDB connection from local environment

## 3. Scraper Module - Base
- [ ] 3.1 Create `scraper/` directory
- [ ] 3.2 Implement `scraper/base.py` with BaseScraper class
  - HTTP request wrapper with retry logic
  - User-Agent configuration
  - Encoding detection
  - Rate limiting (1 second delay)
  - Error handling
- [ ] 3.3 Write unit tests for BaseScraper
- [ ] 3.4 Test with actual netkeiba URLs

## 4. Scraper Module - Race
- [ ] 4.1 Implement `scraper/race.py` with RaceScraper class
- [ ] 4.2 Implement fetch_races_by_date() method
  - Fetch race list page
  - Extract race_ids with track names and race numbers
  - Return structured data
- [ ] 4.3 Implement get_race_id() method
  - Filter races by track name and race number
  - Return specific race_id
- [ ] 4.4 Implement fetch_race_details() method
  - Fetch race details page
  - Extract distance, track type
  - Extract horse list with horse_ids and jockey_ids
  - Return structured race data
- [ ] 4.5 Write unit tests with mock HTML
- [ ] 4.6 Test with actual race URLs from different dates

## 5. Scraper Module - Horse
- [ ] 5.1 Implement `scraper/horse.py` with HorseScraper class
- [ ] 5.2 Implement fetch_horse_results() method
  - Fetch horse detail page
  - Extract past race results table
  - Parse race dates, positions, times, distances
  - Calculate days since last race
  - Return structured data
- [ ] 5.3 Implement fetch_parent_horses() method
  - Extract parent horse IDs
  - Fetch sire and dam data
  - Extract earnings and career records
  - Return structured parent data
- [ ] 5.4 Write unit tests
- [ ] 5.5 Test with actual horse IDs

## 6. Scraper Module - Jockey
- [ ] 6.1 Implement `scraper/jockey.py` with JockeyScraper class
- [ ] 6.2 Implement fetch_jockey_stats() method
  - Fetch jockey detail page
  - Identify statistics table
  - Extract recent 5-year win rate and place rate
  - Calculate averages
  - Return structured data
- [ ] 6.3 Write unit tests
- [ ] 6.4 Test with actual jockey IDs

## 7. Cache Module
- [ ] 7.1 Create `cache/` directory
- [ ] 7.2 Implement `cache/dynamodb.py` with DynamoDBCache class
- [ ] 7.3 Implement get() method (fetch from cache)
- [ ] 7.4 Implement set() method (store with TTL)
- [ ] 7.5 Implement cache key generation for different data types
- [ ] 7.6 Add error handling for DynamoDB failures
- [ ] 7.7 Write unit tests with mocked boto3
- [ ] 7.8 Integration test with actual DynamoDB table

## 8. LLM Analyzer Module
- [ ] 8.1 Create `analyzer/` directory
- [ ] 8.2 Create `analyzer/prompts.py` with prompt templates
  - System prompt
  - User prompt template
  - Data formatting helpers
- [ ] 8.3 Implement `analyzer/gpt_analyzer.py` with GPTAnalyzer class
- [ ] 8.4 Implement analyze_horses() method
  - Format race data
  - Construct prompts
  - Call GPT-5 API
  - Parse response
  - Return structured analysis (individual, comparison, ranking)
- [ ] 8.5 Implement token counting and logging
- [ ] 8.6 Add retry logic for API errors
- [ ] 8.7 Write unit tests with mocked OpenAI API
- [ ] 8.8 Test with actual GPT-5 API (small dataset)

## 9. Streamlit UI - Authentication
- [ ] 9.1 Create `app.py` as main Streamlit application
- [ ] 9.2 Implement authentication check using session state
- [ ] 9.3 Create login UI with password input
- [ ] 9.4 Validate password against environment variable
- [ ] 9.5 Test authentication flow

## 10. Streamlit UI - Race Selection
- [ ] 10.1 Implement race date input (text input or date picker)
- [ ] 10.2 Fetch available races when date is selected
- [ ] 10.3 Populate track name dropdown from available races
- [ ] 10.4 Populate race number dropdown when track is selected
- [ ] 10.5 Display loading spinner during data fetching
- [ ] 10.6 Add error handling for invalid dates or no races found

## 11. Streamlit UI - Analysis Trigger
- [ ] 11.1 Add custom prompt text area (optional)
- [ ] 11.2 Add "解析開始" button
- [ ] 11.3 Validate selections before starting analysis
- [ ] 11.4 Show progress indicator with steps:
  - データ取得中...
  - LLM解析中...
- [ ] 11.5 Display estimated time remaining

## 12. Streamlit UI - Results Display
- [ ] 12.1 Create tabbed interface with 3 tabs
- [ ] 12.2 Tab 1: Display individual horse analysis
  - Show each horse's name
  - Display strengths and weaknesses
  - Use expandable sections for mobile readability
- [ ] 12.3 Tab 2: Display comparison analysis
  - Show head-to-head comparisons
  - Use collapsible sections
- [ ] 12.4 Tab 3: Display recommendation ranking
  - Show top 5 horses in ranked order
  - Display reasoning for each
- [ ] 12.5 Ensure mobile responsiveness (test on phone)
- [ ] 12.6 Add download button for results (optional)

## 13. Integration & End-to-End Testing
- [ ] 13.1 Integration test: Full flow from date selection to results
- [ ] 13.2 Test cache hit/miss scenarios
- [ ] 13.3 Test with different race dates and tracks
- [ ] 13.4 Test error scenarios (invalid date, network errors, etc.)
- [ ] 13.5 Performance test: Measure response times
- [ ] 13.6 Test on mobile device (iOS/Android)

## 14. Docker Configuration
- [ ] 14.1 Create Dockerfile
- [ ] 14.2 Build Docker image locally
- [ ] 14.3 Test running container locally
- [ ] 14.4 Optimize image size (use slim base image)
- [ ] 14.5 Add healthcheck endpoint

## 15. AWS Deployment
- [ ] 15.1 Create ECR repository
- [ ] 15.2 Push Docker image to ECR
- [ ] 15.3 Create App Runner service
- [ ] 15.4 Configure environment variables in App Runner:
  - OPENAI_API_KEY
  - APP_PASSWORD
  - AWS_REGION
  - DYNAMODB_TABLE
- [ ] 15.5 Configure IAM role for DynamoDB access
- [ ] 15.6 Set CPU/Memory to minimum (0.25vCPU, 0.5GB)
- [ ] 15.7 Deploy and test

## 16. Documentation
- [ ] 16.1 Write README.md with:
  - Project overview
  - Setup instructions
  - Environment variables
  - Running locally
  - Deployment guide
- [ ] 16.2 Document API costs and usage
- [ ] 16.3 Create troubleshooting guide
- [ ] 16.4 Document known limitations

## 17. Final Testing & Launch
- [ ] 17.1 Test deployed application end-to-end
- [ ] 17.2 Verify all environment variables are set
- [ ] 17.3 Test on multiple mobile devices
- [ ] 17.4 Monitor CloudWatch logs for errors
- [ ] 17.5 Verify DynamoDB caching is working
- [ ] 17.6 Test with real race on target date
- [ ] 17.7 Share URL with users

## 18. Post-Launch Monitoring
- [ ] 18.1 Monitor AWS costs (App Runner, DynamoDB, API calls)
- [ ] 18.2 Check CloudWatch logs for errors
- [ ] 18.3 Gather user feedback
- [ ] 18.4 Adjust cache TTL if needed
- [ ] 18.5 Optimize GPT-5 prompts based on results quality
