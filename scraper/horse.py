"""
Horse scraper module for netkeiba.com
Handles fetching horse performance data and parent horse information.
"""

from typing import Dict, List, Optional
from datetime import datetime
import re
from .base import BaseScraper


class HorseScraper(BaseScraper):
    """Scraper for horse information from netkeiba.com"""

    BASE_URL = "https://db.netkeiba.com"

    def __init__(self):
        """Initialize horse scraper"""
        super().__init__()

    def fetch_horse_results(self, horse_id: str) -> Optional[Dict]:
        """
        Fetch past race results for a specific horse

        Args:
            horse_id: Horse identifier

        Returns:
            Dictionary containing:
            - horse_id: str
            - horse_name: str
            - recent_results: List[Dict] - Past race results (most recent first)
                - date: str
                - track: str
                - distance: str
                - position: int
                - time: str
                - margin: str
            - days_since_last_race: int
        """
        url = f"{self.BASE_URL}/horse/result/{horse_id}/"

        soup = self.fetch(url)
        if not soup:
            return None

        # Extract horse name
        horse_name = self.safe_extract_text(soup, '.horse_title h1', '')

        # Extract race results table
        results_table = soup.select_one('.db_h_race_results')
        if not results_table:
            return {
                'horse_id': horse_id,
                'horse_name': horse_name,
                'recent_results': [],
                'days_since_last_race': 999
            }

        results = []
        result_rows = results_table.select('tbody tr')

        for row in result_rows[:10]:  # Get latest 10 races
            # Column mapping based on actual HTML structure:
            # 0: 日付, 1: 開催, 2: 天気, 3: R, 4: レース名,
            # 11: 着順, 14: 距離, 18: タイム, 19: 着差

            # Extract date (Column 0)
            date_str = self.safe_extract_text(row, 'td:nth-of-type(1)', '')

            # Extract track name (Column 1)
            track_name = self.safe_extract_text(row, 'td:nth-of-type(2) a', '')
            if not track_name:
                track_name = self.safe_extract_text(row, 'td:nth-of-type(2)', '')

            # Extract distance and track type (Column 14)
            distance_data = self.safe_extract_text(row, 'td:nth-of-type(15)', '')

            # Extract position (Column 11)
            position_str = self.safe_extract_text(row, 'td:nth-of-type(12)', '0')
            position = self._parse_position(position_str)

            # Extract time (Column 18)
            time_str = self.safe_extract_text(row, 'td:nth-of-type(19)', '')

            # Extract margin (Column 19)
            margin = self.safe_extract_text(row, 'td:nth-of-type(20)', '')

            results.append({
                'date': date_str,
                'track': track_name,
                'distance': distance_data,
                'position': position,
                'time': time_str,
                'margin': margin
            })

        # Calculate days since last race
        days_since_last_race = self._calculate_days_since_last_race(results)

        return {
            'horse_id': horse_id,
            'horse_name': horse_name,
            'recent_results': results,
            'days_since_last_race': days_since_last_race
        }

    def fetch_parent_horses(self, horse_id: str) -> Optional[Dict]:
        """
        Fetch parent horse information (sire and dam)

        Args:
            horse_id: Horse identifier

        Returns:
            Dictionary containing:
            - horse_id: str
            - sire: Dict - Father horse info
                - name: str
                - id: str
                - earnings: str (e.g., "1,234,567,890")
                - first: int (1着回数)
                - second: int (2着回数)
                - third: int (3着回数)
                - fourth_or_lower: int (4着以降回数)
            - dam: Dict - Mother horse info
                - name: str
                - id: str
                - earnings: str
                - first: int
                - second: int
                - third: int
                - fourth_or_lower: int
        """
        # Access pedigree page
        url = f"{self.BASE_URL}/horse/ped/{horse_id}/"

        soup = self.fetch(url)
        if not soup:
            return None

        # Extract pedigree information from blood_table
        blood_table = soup.select_one('.blood_table')
        sire_info = {'name': '', 'id': '', 'earnings': '', 'first': 0, 'second': 0, 'third': 0, 'fourth_or_lower': 0}
        dam_info = {'name': '', 'id': '', 'earnings': '', 'first': 0, 'second': 0, 'third': 0, 'fourth_or_lower': 0}

        if blood_table:
            rows = blood_table.select('tr')

            # First row, first cell is sire (father)
            if len(rows) > 0:
                first_cell = rows[0].select_one('td a')
                if first_cell:
                    sire_info['name'] = first_cell.get_text(strip=True)
                    sire_href = first_cell.get('href', '')
                    sire_info['id'] = self._extract_horse_id_from_url(sire_href)

            # Dam (mother) is around row 8-9, first cell
            for i, row in enumerate(rows):
                if i >= 8:
                    cells = row.select('td')
                    if len(cells) > 0:
                        first_cell = cells[0].select_one('a')
                        if first_cell:
                            href = first_cell.get('href', '')
                            horse_id_candidate = self._extract_horse_id_from_url(href)
                            # Check if horse_id starts with 19xx or 20xx (born year)
                            if horse_id_candidate and (
                                horse_id_candidate.startswith('19') or
                                horse_id_candidate.startswith('20')
                            ):
                                dam_info['name'] = first_cell.get_text(strip=True)
                                dam_info['id'] = horse_id_candidate
                                break

        # Fetch detailed stats for sire
        if sire_info['id']:
            sire_stats = self._fetch_parent_details(sire_info['id'])
            if sire_stats:
                sire_info['earnings'] = sire_stats.get('earnings', '')
                sire_info['first'] = sire_stats.get('first', 0)
                sire_info['second'] = sire_stats.get('second', 0)
                sire_info['third'] = sire_stats.get('third', 0)
                sire_info['fourth_or_lower'] = sire_stats.get('fourth_or_lower', 0)

        # Fetch detailed stats for dam
        if dam_info['id']:
            dam_stats = self._fetch_parent_details(dam_info['id'])
            if dam_stats:
                dam_info['earnings'] = dam_stats.get('earnings', '')
                dam_info['first'] = dam_stats.get('first', 0)
                dam_info['second'] = dam_stats.get('second', 0)
                dam_info['third'] = dam_stats.get('third', 0)
                dam_info['fourth_or_lower'] = dam_stats.get('fourth_or_lower', 0)

        return {
            'horse_id': horse_id,
            'sire': sire_info,
            'dam': dam_info
        }


    def _extract_horse_id_from_url(self, url: str) -> str:
        """
        Extract horse ID from a netkeiba URL

        Args:
            url: URL string

        Returns:
            Horse ID string or empty string
        """
        if not url or '/horse/' not in url:
            return ""

        parts = url.strip('/').split('/')
        try:
            horse_index = parts.index('horse')
            if horse_index + 1 < len(parts):
                return parts[horse_index + 1]
        except (ValueError, IndexError):
            pass

        return ""

    def _fetch_parent_details(self, parent_id: str) -> Optional[Dict]:
        """
        Fetch detailed information for a parent horse (earnings and record)

        Args:
            parent_id: Parent horse identifier

        Returns:
            Dictionary containing:
            - earnings: str (e.g., "1,234,567,890")
            - first: int (1着回数)
            - second: int (2着回数)
            - third: int (3着回数)
            - fourth_or_lower: int (4着以降回数)
            Returns None if fetching fails
        """
        url = f"{self.BASE_URL}/horse/{parent_id}/"
        soup = self.fetch(url)
        if not soup:
            return None

        earnings = ""
        first = 0
        second = 0
        third = 0
        fourth_or_lower = 0

        # Extract from profile table
        profile_table = soup.select_one('.db_prof_table')
        if profile_table:
            rows = profile_table.select('tr')
            for row in rows:
                th = row.select_one('th')
                td = row.select_one('td')

                if th and td:
                    header = th.get_text(strip=True)
                    value = td.get_text(strip=True)

                    # Extract earnings (獲得賞金)
                    if '獲得賞金' in header:
                        earnings = value

                    # Extract record (通算成績)
                    # Format: "12戦12勝 [12-10-5-3]" -> extract each value
                    if '通算成績' in header:
                        # Extract bracketed values [1着-2着-3着-4着以降]
                        bracket_match = re.search(r'\[(\d+)-(\d+)-(\d+)-(\d+)\]', value)
                        if bracket_match:
                            first = int(bracket_match.group(1))
                            second = int(bracket_match.group(2))
                            third = int(bracket_match.group(3))
                            fourth_or_lower = int(bracket_match.group(4))

        return {
            'earnings': earnings,
            'first': first,
            'second': second,
            'third': third,
            'fourth_or_lower': fourth_or_lower
        }

    def _parse_position(self, position_str: str) -> int:
        """
        Parse position string to integer

        Args:
            position_str: Position string (may contain non-numeric characters)

        Returns:
            Position as integer, or 99 if parsing fails
        """
        if not position_str:
            return 99

        # Remove non-numeric characters
        numeric_part = ''.join(filter(str.isdigit, position_str))

        if numeric_part:
            return int(numeric_part)

        return 99

    def fetch_overall_stats(self, horse_id: str) -> Optional[Dict]:
        """
        Fetch overall statistics for a horse

        Args:
            horse_id: Horse identifier

        Returns:
            Dictionary containing:
            - horse_id: str
            - horse_name: str
            - overall_record: str (e.g., "2戦0勝 [0-0-0-2]")
            - wins: int
            - races: int
        """
        url = f"{self.BASE_URL}/horse/{horse_id}/"
        soup = self.fetch(url)
        if not soup:
            return None

        # Extract horse name
        horse_name_elem = soup.select_one('.horse_title h1')
        horse_name = horse_name_elem.get_text(strip=True) if horse_name_elem else ""

        # Extract overall record from profile table
        profile_table = soup.select_one('.db_prof_table')
        overall_record = ""
        wins = 0
        races = 0

        if profile_table:
            rows = profile_table.select('tr')
            for row in rows:
                th = row.select_one('th')
                td = row.select_one('td')

                if th and td:
                    header = th.get_text(strip=True)
                    if '通算成績' in header:
                        overall_record = td.get_text(strip=True)

                        # Extract races: "2戦0勝 [0-0-0-2]"
                        races_match = re.search(r'(\d+)戦', overall_record)
                        if races_match:
                            races = int(races_match.group(1))

                        # Extract wins
                        wins_match = re.search(r'(\d+)勝', overall_record)
                        if wins_match:
                            wins = int(wins_match.group(1))

                        break

        return {
            'horse_id': horse_id,
            'horse_name': horse_name,
            'overall_record': overall_record,
            'wins': wins,
            'races': races
        }

    def fetch_race_results(self, horse_id: str, limit: int = None) -> Optional[Dict]:
        """
        Fetch all race results for a horse

        Args:
            horse_id: Horse identifier
            limit: Maximum number of races to fetch (None = all)

        Returns:
            Dictionary containing:
            - horse_id: str
            - results: List[Dict] - Race results with all available data
        """
        url = f"{self.BASE_URL}/horse/result/{horse_id}/"
        soup = self.fetch(url)
        if not soup:
            return None

        # Find race results table
        race_results_table = soup.select_one('.db_h_race_results')
        if not race_results_table:
            return {
                'horse_id': horse_id,
                'results': []
            }

        results = []
        data_rows = race_results_table.select('tbody tr')

        # Apply limit if specified
        if limit:
            data_rows = data_rows[:limit]

        for row in data_rows:
            cells = row.select('td')

            if len(cells) < 20:
                continue

            # Extract all data from cells
            race_data = {
                'date': self._get_cell_text(cells, 0),
                'venue': self._get_cell_text(cells, 1),
                'weather': self._get_cell_text(cells, 2),
                'race_number': self._get_cell_text(cells, 3),
                'race_name': self._get_cell_text(cells, 4),
                'num_horses': self._get_cell_text(cells, 6),
                'gate_number': self._get_cell_text(cells, 7),
                'horse_number': self._get_cell_text(cells, 8),
                'odds': self._get_cell_text(cells, 9),
                'popularity': self._get_cell_text(cells, 10),
                'finish_position': self._get_cell_text(cells, 11),
                'jockey': self._get_cell_text(cells, 12),
                'weight': self._get_cell_text(cells, 13),
                'distance': self._get_cell_text(cells, 14),
                'track_condition': self._get_cell_text(cells, 16),
                'track_index': self._get_cell_text(cells, 17),
                'time': self._get_cell_text(cells, 18),
                'margin': self._get_cell_text(cells, 19),
                'time_index': self._get_cell_text(cells, 20) if len(cells) > 20 else '',
                'passing': self._get_cell_text(cells, 21) if len(cells) > 21 else '',
                'pace': self._get_cell_text(cells, 22) if len(cells) > 22 else '',
                'last_3f': self._get_cell_text(cells, 23) if len(cells) > 23 else '',
                'horse_weight': self._get_cell_text(cells, 24) if len(cells) > 24 else '',
                'trainer_comment': self._get_cell_text(cells, 25) if len(cells) > 25 else '',
                'note': self._get_cell_text(cells, 26) if len(cells) > 26 else '',
                'winner': self._get_cell_text(cells, 27) if len(cells) > 27 else '',
                'prize': self._get_cell_text(cells, 28) if len(cells) > 28 else '',
            }

            # Parse distance to extract track type and distance in meters
            distance_info = self._parse_distance(race_data['distance'])
            race_data['track_type'] = distance_info['track_type']
            race_data['distance_meters'] = distance_info['distance_meters']

            results.append(race_data)

        return {
            'horse_id': horse_id,
            'results': results
        }

    def _get_cell_text(self, cells, index):
        """Safely extract text from a cell"""
        if index < len(cells):
            return cells[index].get_text(strip=True)
        return ''

    def _parse_distance(self, distance_str: str) -> Dict:
        """
        Parse distance string

        Args:
            distance_str: Distance string (e.g., "ダ1500", "芝2000")

        Returns:
            Dict with track_type and distance_meters
        """
        track_type = ''
        distance_meters = 0

        if not distance_str:
            return {'track_type': track_type, 'distance_meters': distance_meters}

        # Determine track type
        if '芝' in distance_str:
            track_type = '芝'
        elif 'ダ' in distance_str:
            track_type = 'ダート'
        elif '障' in distance_str:
            track_type = '障害'

        # Extract distance (numeric part)
        match = re.search(r'(\d+)', distance_str)
        if match:
            distance_meters = int(match.group(1))

        return {
            'track_type': track_type,
            'distance_meters': distance_meters
        }

    def _calculate_days_since_last_race(self, results: List[Dict]) -> int:
        """
        Calculate days since the most recent race

        Args:
            results: List of race results

        Returns:
            Number of days since last race, or 999 if no results
        """
        if not results:
            return 999

        try:
            # Get the most recent race date
            last_race_date_str = results[0]['date']

            # Parse date (format: YYYY/MM/DD or YYYY.MM.DD)
            last_race_date_str = last_race_date_str.replace('.', '/').replace('-', '/')

            last_race_date = datetime.strptime(last_race_date_str, '%Y/%m/%d')
            current_date = datetime.now()

            days_diff = (current_date - last_race_date).days

            return days_diff

        except (ValueError, IndexError, KeyError):
            return 999
