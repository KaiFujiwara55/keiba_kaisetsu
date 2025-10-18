"""
Test the AJAX endpoint that loads race data
"""
import requests
from bs4 import BeautifulSoup
import json

def test_ajax_endpoint():
    """Test the race_list_get_date_list.html AJAX endpoint"""

    base_url = "https://race.netkeiba.com/top"
    ajax_url = f"{base_url}/race_list_get_date_list.html"

    date = "20251018"

    print(f"Testing AJAX endpoint: {ajax_url}")
    print(f"Date: {date}")
    print("=" * 80)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest'  # AJAX header
    }

    params = {
        'kaisai_date': date,
        'encoding': 'UTF-8'
    }

    try:
        response = requests.get(ajax_url, headers=headers, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)}")
        print("=" * 80)

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            return

        # Save response
        output_file = "/Users/kai/programing/keiba_kaisetsu/debug/ajax_response.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Saved response to: {output_file}")

        # Parse the response
        soup = BeautifulSoup(response.content, 'html.parser')

        print("\n" + "=" * 80)
        print("Analyzing AJAX response:")
        print("=" * 80)

        # Look for race data
        race_links = soup.find_all('a', href=lambda x: x and 'race_id=' in x)
        print(f"\nFound {len(race_links)} race links")

        if race_links:
            print("\nFirst 5 race links:")
            for i, link in enumerate(race_links[:5]):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                parent = link.parent
                parent_class = parent.get('class') if parent else None
                print(f"  {i+1}. '{text[:40]}' | {href}")
                print(f"     Parent: <{parent.name}> class={parent_class}")

        # Look for specific class patterns
        print("\n" + "=" * 80)
        print("Checking for RaceList classes:")
        print("=" * 80)

        race_list_elements = soup.find_all(class_=lambda x: x and 'RaceList' in str(x))
        print(f"Found {len(race_list_elements)} elements with 'RaceList' in class")

        class_names = set()
        for elem in race_list_elements:
            classes = elem.get('class', [])
            for cls in classes:
                if 'RaceList' in cls:
                    class_names.add(cls)

        print("Unique class names:")
        for cls in sorted(class_names):
            count = len(soup.find_all(class_=cls))
            print(f"  .{cls}: {count} elements")

        # Show structure
        if race_list_elements:
            print("\n" + "=" * 80)
            print("Sample structure:")
            print("=" * 80)
            first = race_list_elements[0]
            print(f"Tag: {first.name}")
            print(f"Classes: {first.get('class')}")
            print(f"HTML preview (first 500 chars):")
            print(str(first)[:500])

    except requests.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ajax_endpoint()
