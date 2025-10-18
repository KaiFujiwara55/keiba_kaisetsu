"""
Base scraper module for netkeiba.com
Provides common HTTP request functionality with retry logic, rate limiting, and error handling.
"""

import time
import os
from typing import Optional
import requests
from bs4 import BeautifulSoup


class BaseScraper:
    """Base class for all netkeiba scrapers"""

    # Configuration from environment variables
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    def __init__(self):
        """Initialize base scraper with configuration"""
        self.timeout = int(os.getenv('REQUEST_TIMEOUT', '10'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.delay = float(os.getenv('SCRAPING_DELAY_SECONDS', '1.0'))
        self.last_request_time = 0

    def _rate_limit(self):
        """Ensure minimum delay between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.delay:
            sleep_time = self.delay - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _detect_encoding(self, response: requests.Response) -> str:
        """
        Detect proper encoding for the response

        Args:
            response: requests Response object

        Returns:
            Detected encoding string
        """
        # Try apparent_encoding first
        if response.apparent_encoding:
            return response.apparent_encoding

        # Fallback to common Japanese encodings
        for encoding in ['euc-jp', 'shift_jis', 'utf-8']:
            try:
                response.content.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue

        # Default to utf-8
        return 'utf-8'

    def fetch(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse HTML from a URL with retry logic

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if failed after retries

        Raises:
            Exception: If all retry attempts fail
        """
        # Apply rate limiting
        self._rate_limit()

        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self.HEADERS,
                    timeout=self.timeout
                )

                # Check for HTTP errors
                response.raise_for_status()

                # Detect and set proper encoding
                encoding = self._detect_encoding(response)
                response.encoding = encoding

                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                return soup

            except requests.exceptions.Timeout as e:
                last_error = e
                print(f"Timeout error on attempt {attempt + 1}/{self.max_retries}: {url}")

            except requests.exceptions.HTTPError as e:
                # Don't retry on 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    print(f"Client error {e.response.status_code}: {url}")
                    raise

                last_error = e
                print(f"HTTP error on attempt {attempt + 1}/{self.max_retries}: {e}")

            except requests.exceptions.RequestException as e:
                last_error = e
                print(f"Request error on attempt {attempt + 1}/{self.max_retries}: {e}")

            except Exception as e:
                last_error = e
                print(f"Unexpected error on attempt {attempt + 1}/{self.max_retries}: {e}")

            # Wait before retrying (exponential backoff)
            if attempt < self.max_retries - 1:
                wait_time = self.delay * (2 ** attempt)
                print(f"Waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)

        # All retries failed
        print(f"Failed to fetch after {self.max_retries} attempts: {url}")
        if last_error:
            raise Exception(f"Failed to fetch {url}: {last_error}")

        return None

    def safe_extract_text(self, element, selector: str, default: str = "") -> str:
        """
        Safely extract text from an element using CSS selector

        Args:
            element: BeautifulSoup element to search in
            selector: CSS selector
            default: Default value if element not found

        Returns:
            Extracted text or default value
        """
        if element is None:
            return default

        found = element.select_one(selector)
        if found:
            return found.get_text(strip=True)

        return default

    def safe_extract_attr(self, element, selector: str, attr: str, default: str = "") -> str:
        """
        Safely extract attribute from an element using CSS selector

        Args:
            element: BeautifulSoup element to search in
            selector: CSS selector
            attr: Attribute name to extract
            default: Default value if element not found

        Returns:
            Extracted attribute value or default value
        """
        if element is None:
            return default

        found = element.select_one(selector)
        if found and found.has_attr(attr):
            return found[attr]

        return default
