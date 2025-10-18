"""
Jockey scraper module for netkeiba.com
Handles fetching jockey performance statistics.
"""

from typing import Dict, Optional
import re
from .base import BaseScraper


class JockeyScraper(BaseScraper):
    """Scraper for jockey information from netkeiba.com"""

    BASE_URL = "https://db.netkeiba.com"

    def __init__(self):
        """Initialize jockey scraper"""
        super().__init__()

    def fetch_jockey_stats(self, jockey_id: str) -> Optional[Dict]:
        """
        Fetch jockey performance statistics

        Args:
            jockey_id: Jockey identifier

        Returns:
            Dictionary containing:
            - jockey_id: str
            - jockey_name: str
            - overall_stats: Dict - Overall cumulative statistics
                - win_rate: float
                - place_rate: float
                - show_rate: float
                - wins: int
                - seconds: int
                - thirds: int
                - total_races: int
            - recent_5year_stats: Dict - Recent 5-year statistics
                - win_rate: float
                - place_rate: float
                - show_rate: float
                - wins: int
                - seconds: int
                - thirds: int
                - total_races: int
        """
        url = f"{self.BASE_URL}/jockey/{jockey_id}/"

        soup = self.fetch(url)
        if not soup:
            return None

        # Extract jockey name
        jockey_name_elem = soup.select_one('.db_head_name h1')
        jockey_name = ""
        if jockey_name_elem:
            # Clean up whitespace
            jockey_name = re.sub(r'\s+', ' ', jockey_name_elem.get_text(strip=True))

        # Find ResultsByYears tables
        results_tables = soup.select('table.ResultsByYears')

        overall_stats = {
            'win_rate': 0.0,
            'place_rate': 0.0,
            'show_rate': 0.0,
            'wins': 0,
            'seconds': 0,
            'thirds': 0,
            'total_races': 0
        }

        recent_5year_stats = {
            'win_rate': 0.0,
            'place_rate': 0.0,
            'show_rate': 0.0,
            'wins': 0,
            'seconds': 0,
            'thirds': 0,
            'total_races': 0
        }

        # Use first table (central racing)
        if results_tables and len(results_tables) > 0:
            table = results_tables[0]
            tbody = table.select_one('tbody')

            if tbody:
                rows = tbody.select('tr')

                # First row is cumulative stats
                if len(rows) > 0:
                    cumulative_row = rows[0]
                    first_cell = cumulative_row.select_one('td')
                    if first_cell and '累計' in first_cell.get_text(strip=True):
                        overall_stats = self._parse_stats_row(cumulative_row)

                # Get recent 5 years (rows 1-5, excluding cumulative row)
                year_rows = [row for row in rows[1:6] if self._is_year_row(row)]
                if year_rows:
                    recent_5year_stats = self._aggregate_year_stats(year_rows)

        return {
            'jockey_id': jockey_id,
            'jockey_name': jockey_name,
            'overall_stats': overall_stats,
            'recent_5year_stats': recent_5year_stats
        }

    def _is_year_row(self, row):
        """Check if row contains year data"""
        first_cell = row.select_one('td')
        if not first_cell:
            return False

        text = first_cell.get_text(strip=True)
        # Check if it's a 4-digit year (2020-2030, etc.)
        return bool(re.match(r'^20\d{2}$', text))

    def _parse_stats_row(self, row):
        """
        Parse a statistics row

        Table columns:
        0: Year, 1: Rank, 2: 1st, 3: 2nd, 4: 3rd, 5: 4th~, 6: Total races,
        7: G races, 8: G wins, 9: Win rate, 10: Place rate, 11: Show rate, 12: Top horse
        """
        cells = row.select('td')

        stats = {
            'wins': 0,
            'seconds': 0,
            'thirds': 0,
            'total_races': 0,
            'win_rate': 0.0,
            'place_rate': 0.0,
            'show_rate': 0.0
        }

        if len(cells) < 12:
            return stats

        # Extract data from cells
        stats['wins'] = self._parse_int(cells[2].get_text(strip=True))
        stats['seconds'] = self._parse_int(cells[3].get_text(strip=True))
        stats['thirds'] = self._parse_int(cells[4].get_text(strip=True))
        stats['total_races'] = self._parse_int(cells[6].get_text(strip=True))
        stats['win_rate'] = self._parse_percentage(cells[9].get_text(strip=True))
        stats['place_rate'] = self._parse_percentage(cells[10].get_text(strip=True))
        stats['show_rate'] = self._parse_percentage(cells[11].get_text(strip=True))

        return stats

    def _aggregate_year_stats(self, year_rows):
        """
        Aggregate statistics from multiple years

        Args:
            year_rows: List of year rows

        Returns:
            Aggregated statistics
        """
        total_wins = 0
        total_seconds = 0
        total_thirds = 0
        total_races = 0

        for row in year_rows:
            stats = self._parse_stats_row(row)
            total_wins += stats['wins']
            total_seconds += stats['seconds']
            total_thirds += stats['thirds']
            total_races += stats['total_races']

        # Calculate rates
        win_rate = 0.0
        place_rate = 0.0
        show_rate = 0.0

        if total_races > 0:
            win_rate = round((total_wins / total_races) * 100, 1)
            place_rate = round(((total_wins + total_seconds) / total_races) * 100, 1)
            show_rate = round(((total_wins + total_seconds + total_thirds) / total_races) * 100, 1)

        return {
            'wins': total_wins,
            'seconds': total_seconds,
            'thirds': total_thirds,
            'total_races': total_races,
            'win_rate': win_rate,
            'place_rate': place_rate,
            'show_rate': show_rate
        }

    def _parse_percentage(self, percentage_str: str) -> float:
        """
        Parse percentage string to float

        Args:
            percentage_str: Percentage string (e.g., "15.5%" or "15.5")

        Returns:
            Percentage as float
        """
        if not percentage_str:
            return 0.0

        # Remove % sign (both half-width and full-width) and whitespace
        clean_str = percentage_str.replace('%', '').replace('％', '').strip()

        try:
            return float(clean_str)
        except ValueError:
            return 0.0

    def _parse_int(self, int_str: str) -> int:
        """
        Parse integer string, handling Japanese numerals

        Args:
            int_str: Integer string

        Returns:
            Integer value, or 0 if parsing fails
        """
        if not int_str:
            return 0

        # Remove whitespace and commas
        clean_str = int_str.replace(',', '').strip()

        # Extract only digits
        numeric_part = ''.join(filter(str.isdigit, clean_str))

        if numeric_part:
            return int(numeric_part)

        return 0
