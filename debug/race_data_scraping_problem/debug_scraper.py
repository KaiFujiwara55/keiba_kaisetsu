"""
Debug script to investigate race.py scraping issues
"""
import requests
from bs4 import BeautifulSoup
import sys

def debug_race_scraper():
    """Debug the race scraper with the specified URL"""
    url = "https://race.netkeiba.com/top/race_list.html?kaisai_date=20251018"

    print(f"Fetching URL: {url}")
    print("=" * 80)

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)}")
        print("=" * 80)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Test 1: Check for .RaceList_DataList
        print("\n[Test 1] Checking for '.RaceList_DataList' selector:")
        race_list_sections = soup.select('.RaceList_DataList')
        print(f"Found {len(race_list_sections)} elements with class 'RaceList_DataList'")

        # Test 2: Find all elements with "RaceList" in class name
        print("\n[Test 2] Finding all elements with 'RaceList' in class name:")
        all_racelist_elements = soup.find_all(class_=lambda x: x and 'RaceList' in x)
        print(f"Found {len(all_racelist_elements)} elements")

        # Get unique class names
        class_names = set()
        for elem in all_racelist_elements:
            classes = elem.get('class', [])
            for cls in classes:
                if 'RaceList' in cls:
                    class_names.add(cls)

        print("Unique class names containing 'RaceList':")
        for cls in sorted(class_names):
            count = len(soup.find_all(class_=cls))
            print(f"  .{cls}: {count} elements")

        # Test 3: Check structure - print first few elements
        print("\n[Test 3] Sample HTML structure:")
        if all_racelist_elements:
            print(f"\nFirst element with RaceList class:")
            first_elem = all_racelist_elements[0]
            print(f"  Tag: {first_elem.name}")
            print(f"  Classes: {first_elem.get('class')}")
            print(f"  First 200 chars of HTML:")
            print(f"  {str(first_elem)[:200]}...")

        # Test 4: Look for race links
        print("\n[Test 4] Looking for race links:")
        race_links = soup.find_all('a', href=lambda x: x and 'race_id=' in x)
        print(f"Found {len(race_links)} links with 'race_id=' in href")

        if race_links:
            print(f"\nFirst 3 race links:")
            for i, link in enumerate(race_links[:3]):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"  {i+1}. Text: '{text[:30]}' | Href: {href}")
                # Show parent structure
                parent = link.parent
                if parent:
                    print(f"     Parent: <{parent.name}> classes={parent.get('class')}")

        # Test 5: Check for common alternative structures
        print("\n[Test 5] Checking alternative selectors:")

        selectors_to_try = [
            '.RaceList_DataList',
            '.RaceList_Data',
            '.RaceListData',
            'ul.RaceList',
            'div.RaceList',
            '.race-list',
            '.raceList'
        ]

        for selector in selectors_to_try:
            elements = soup.select(selector)
            print(f"  {selector}: {len(elements)} elements")

        # Test 6: Save HTML snippet for manual inspection
        print("\n[Test 6] Saving HTML snippet for manual inspection:")

        # Save first 10000 chars of HTML
        output_file = "/Users/kai/programing/keiba_kaisetsu/debug/debug_html_sample.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()[:10000]))
        print(f"Saved HTML sample to: {output_file}")

        # Test 7: Try to find track/venue information
        print("\n[Test 7] Looking for track/venue information:")
        title_elements = soup.find_all(class_=lambda x: x and 'Title' in str(x))
        print(f"Found {len(title_elements)} elements with 'Title' in class")
        for i, elem in enumerate(title_elements[:5]):
            print(f"  {i+1}. <{elem.name}> classes={elem.get('class')} text='{elem.get_text(strip=True)[:50]}'")

    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    debug_race_scraper()
