"""
Race scraper module for netkeiba.com
Handles fetching race lists and race details including horse and jockey information.
"""

from typing import Dict, List, Optional
from datetime import datetime
from .base import BaseScraper


class RaceScraper(BaseScraper):
    """Scraper for race information from netkeiba.com"""

    BASE_URL = "https://race.netkeiba.com"

    def __init__(self):
        """Initialize race scraper"""
        super().__init__()

    def fetch_races_by_date(self, date: str) -> List[Dict[str, str]]:
        """
        Fetch list of all races on a specific date

        Args:
            date: Date string in YYYYMMDD format (e.g., "20231201")

        Returns:
            List of race dictionaries with keys:
            - race_id: str - Unique race identifier
            - track_name: str - Name of the racing track
            - race_number: int - Race number (1-12)
            - race_name: str - Name of the race
        """
        # Build URL for race calendar (use race_list_sub.html which contains the actual race data)
        url = f"{self.BASE_URL}/top/race_list_sub.html?kaisai_date={date}"

        soup = self.fetch(url)
        if not soup:
            return []

        races = []

        # Find all race entries
        # Netkeiba structure: race list is organized by track (kaisai)
        race_list_sections = soup.select('.RaceList_DataList')

        for section in race_list_sections:
            # Extract track name from the section header
            track_header = section.find('dt', class_='RaceList_DataHeader')
            track_name = ""
            if track_header:
                track_name = self.safe_extract_text(track_header, '.RaceList_DataTitle', '')

            # Find all race items in this section
            race_items = section.select('li.RaceList_DataItem')

            for race_item in race_items:
                # Extract race link
                race_link = race_item.select_one('a')
                if not race_link or not race_link.has_attr('href'):
                    continue

                href = race_link['href']

                # Extract race_id from href
                # Format: /race/shutuba.html?race_id=202305040101
                race_id = self._extract_race_id_from_url(href)
                if not race_id:
                    continue

                # Extract race number from race_id (last 2 digits)
                race_number = int(race_id[-2:])

                # Extract race name
                race_name = self.safe_extract_text(race_item, '.RaceList_ItemTitle .ItemTitle', '')

                races.append({
                    'race_id': race_id,
                    'track_name': track_name,
                    'race_number': race_number,
                    'race_name': race_name
                })

        return races

    def get_race_id(self, date: str, track_name: str, race_number: int) -> Optional[str]:
        """
        Get specific race_id by date, track name, and race number

        Args:
            date: Date string in YYYYMMDD format
            track_name: Name of the racing track
            race_number: Race number (1-12)

        Returns:
            race_id string or None if not found
        """
        races = self.fetch_races_by_date(date)

        for race in races:
            if track_name in race['track_name'] and race['race_number'] == race_number:
                return race['race_id']

        return None

    def fetch_race_details(self, race_id: str, track_name: str = None) -> Optional[Dict]:
        """
        Fetch detailed information about a specific race

        Args:
            race_id: Race identifier (12-digit string)
            track_name: Name of the racing track (optional, will be included in return value if provided)

        Returns:
            Dictionary containing:
            - race_id: str
            - race_name: str
            - distance: str (e.g., "1600m")
            - track_type: str (e.g., "芝", "ダート")
            - track_name: str (if provided in args)
            - horses: List[Dict] - List of horse dictionaries
                - horse_id: str
                - horse_name: str
                - jockey_id: str
                - jockey_name: str
                - frame_number: int
                - horse_number: int
        """
        url = f"{self.BASE_URL}/race/shutuba.html?race_id={race_id}"

        soup = self.fetch(url)
        if not soup:
            return None

        # Extract race metadata
        race_name = self.safe_extract_text(soup, '.RaceName', '')

        # Extract distance and track type from race data
        distance = ""
        track_type = ""

        race_data_elem = soup.select_one('.RaceData01')
        if race_data_elem:
            # 最初のspanタグに距離情報がある
            distance_span = race_data_elem.find('span')
            if distance_span:
                distance_text = distance_span.get_text(strip=True)  # "ダ1600m" or "芝1600m"

                # トラックタイプと距離を分離
                if '芝' in distance_text:
                    track_type = '芝'
                    distance = distance_text.replace('芝', '').strip()
                elif 'ダ' in distance_text:
                    track_type = 'ダート'
                    distance = distance_text.replace('ダート', '').replace('ダ', '').strip()

        # Extract horse entries
        horses = []
        horse_rows = soup.select('tr.HorseList')

        for row in horse_rows:
            # Skip header rows
            if row.find('th'):
                continue

            # Extract frame and horse numbers
            frame_number_elem = row.select_one('td[class^="Waku"]')
            horse_number_elem = row.select_one('td[class^="Umaban"]')

            if not frame_number_elem or not horse_number_elem:
                continue

            frame_number = int(frame_number_elem.get_text(strip=True) or '0')
            horse_number = int(horse_number_elem.get_text(strip=True) or '0')

            # Extract horse info
            horse_link = row.select_one('.HorseInfo a')
            if not horse_link:
                continue

            horse_name = horse_link.get_text(strip=True)
            horse_id = self._extract_id_from_url(horse_link.get('href', ''), 'horse')

            # Extract jockey info
            jockey_link = row.select_one('.Jockey a')
            jockey_name = ""
            jockey_id = ""

            if jockey_link:
                jockey_name = jockey_link.get_text(strip=True)
                jockey_id = self._extract_id_from_url(jockey_link.get('href', ''), 'jockey')

            horses.append({
                'horse_id': horse_id,
                'horse_name': horse_name,
                'jockey_id': jockey_id,
                'jockey_name': jockey_name,
                'frame_number': frame_number,
                'horse_number': horse_number
            })

        result = {
            'race_id': race_id,
            'race_name': race_name,
            'distance': distance,
            'track_type': track_type,
            'horses': horses
        }

        # Include track_name if provided
        if track_name:
            result['track_name'] = track_name

        return result

    def _extract_race_id_from_url(self, url: str) -> Optional[str]:
        """
        Extract race_id from a netkeiba URL

        Args:
            url: URL string

        Returns:
            race_id string or None
        """
        if not url or 'race_id=' not in url:
            return None

        # Extract race_id parameter
        parts = url.split('race_id=')
        if len(parts) < 2:
            return None

        race_id = parts[1].split('&')[0]

        # Validate race_id (should be 12 digits)
        if race_id.isdigit() and len(race_id) == 12:
            return race_id

        return None

    def _extract_id_from_url(self, url: str, entity_type: str) -> str:
        """
        Extract entity ID from a netkeiba URL

        Args:
            url: URL string
            entity_type: Type of entity ('horse', 'jockey', etc.)

        Returns:
            ID string or empty string if not found
        """
        if not url:
            return ""

        # Common URL patterns:
        # /horse/2020104567/
        # /jockey/result/recent/01234/

        parts = url.strip('/').split('/')

        # Find the entity type in the URL
        try:
            type_index = parts.index(entity_type)
            # For jockey, the ID is usually at the end of the path
            # For horse, the ID is right after 'horse'
            if entity_type == 'jockey':
                # Look for the last numeric part after 'jockey'
                for i in range(len(parts) - 1, type_index, -1):
                    if parts[i].isdigit():
                        return parts[i]
            else:
                # For other entities like horse, ID is directly after entity type
                if type_index + 1 < len(parts):
                    return parts[type_index + 1]
        except (ValueError, IndexError):
            pass

        return ""
