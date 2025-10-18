"""
Test the race_list_sub.html endpoint that should contain actual race data
"""
import requests
from bs4 import BeautifulSoup

def test_race_list_sub():
    """Test the race_list_sub.html endpoint"""

    base_url = "https://race.netkeiba.com/top"
    url = f"{base_url}/race_list_sub.html"

    date = "20251018"

    print(f"Testing endpoint: {url}")
    print(f"Date: {date}")
    print("=" * 80)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    params = {
        'kaisai_date': date
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)}")
        print("=" * 80)

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            return

        # Save response
        output_file = "/Users/kai/programing/keiba_kaisetsu/debug/race_list_sub_response.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved response to: {output_file}")

        # Parse
        soup = BeautifulSoup(response.content, 'html.parser')

        print("\n" + "=" * 80)
        print("Analyzing race_list_sub response:")
        print("=" * 80)

        # Look for race links
        race_links = soup.find_all('a', href=lambda x: x and 'race_id=' in x)
        print(f"\nFound {len(race_links)} race links with race_id")

        if race_links:
            print("\nFirst 5 race links:")
            for i, link in enumerate(race_links[:5]):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                parent = link.parent
                parent_class = parent.get('class') if parent else None
                print(f"  {i+1}. Text: '{text[:40]}'")
                print(f"     Href: {href}")
                print(f"     Parent: <{parent.name}> class={parent_class}")
                print()

        # Check for RaceList classes
        print("=" * 80)
        print("Checking for element classes:")
        print("=" * 80)

        # Look for all unique classes
        all_classes = set()
        for elem in soup.find_all(class_=True):
            classes = elem.get('class', [])
            for cls in classes:
                all_classes.add(cls)

        racelist_classes = [cls for cls in all_classes if 'Race' in cls or 'List' in cls]
        print(f"\nClasses containing 'Race' or 'List' ({len(racelist_classes)} total):")
        for cls in sorted(racelist_classes)[:20]:
            count = len(soup.find_all(class_=cls))
            print(f"  .{cls}: {count} elements")

        # Look for track/venue names
        print("\n" + "=" * 80)
        print("Looking for track/venue information:")
        print("=" * 80)

        # Try different selectors
        selectors = [
            '.RaceList_DataTitle',
            '.RaceList_ItemTitle',
            '.RaceKaisai_Title',
            'h3',
            'h4'
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"\n{selector}: {len(elements)} elements")
                for elem in elements[:3]:
                    text = elem.get_text(strip=True)
                    print(f"  - '{text[:50]}'")

    except requests.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_race_list_sub()
