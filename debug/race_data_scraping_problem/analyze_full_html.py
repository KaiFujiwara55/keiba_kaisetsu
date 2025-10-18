"""
Analyze full HTML structure to find race data
"""
import requests
from bs4 import BeautifulSoup
import json

def analyze_html():
    """Analyze the complete HTML structure"""
    url = "https://race.netkeiba.com/top/race_list.html?kaisai_date=20251018"

    print(f"Fetching URL: {url}")
    print("=" * 80)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Save complete HTML
    output_file = "/Users/kai/programing/keiba_kaisetsu/debug/full_html.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print(f"Saved full HTML to: {output_file}")

    # Look for JavaScript data or AJAX endpoints
    print("\n" + "=" * 80)
    print("Searching for JavaScript variables and AJAX endpoints:")
    print("=" * 80)

    scripts = soup.find_all('script')
    print(f"\nFound {len(scripts)} script tags")

    for i, script in enumerate(scripts):
        script_content = script.string
        if script_content:
            # Look for common patterns
            if 'race_id' in script_content.lower():
                print(f"\nScript {i+1} contains 'race_id':")
                lines = script_content.split('\n')
                for line in lines:
                    if 'race_id' in line.lower():
                        print(f"  {line.strip()[:100]}")

            if 'kaisai' in script_content.lower():
                print(f"\nScript {i+1} contains 'kaisai':")
                lines = script_content.split('\n')
                for line in lines[:5]:  # First 5 lines
                    if line.strip():
                        print(f"  {line.strip()[:100]}")

    # Look for data attributes
    print("\n" + "=" * 80)
    print("Looking for data attributes:")
    print("=" * 80)

    elements_with_data = soup.find_all(lambda tag: any(attr.startswith('data-') for attr in tag.attrs))
    print(f"Found {len(elements_with_data)} elements with data-* attributes")

    for elem in elements_with_data[:10]:
        data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
        if data_attrs:
            print(f"  <{elem.name}> {data_attrs}")

    # Look for specific text patterns
    print("\n" + "=" * 80)
    print("Looking for 'レース' text in elements:")
    print("=" * 80)

    race_text_elements = soup.find_all(string=lambda text: text and 'レース' in text)
    print(f"Found {len(race_text_elements)} elements containing 'レース'")

    for text in race_text_elements[:10]:
        parent = text.parent
        if parent:
            print(f"  <{parent.name}> classes={parent.get('class')} text='{str(text).strip()[:50]}'")

if __name__ == "__main__":
    analyze_html()
