"""
Test script to debug fetch_race_details function
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from scraper.race import RaceScraper
import json

def main():
    race_id = "202505040704"
    url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}"

    print(f"Testing fetch_race_details for race_id: {race_id}")
    print(f"URL: {url}")
    print("-" * 80)

    scraper = RaceScraper()

    # First, let's fetch the raw HTML and inspect it
    print("\n1. Fetching HTML...")
    soup = scraper.fetch(url)

    if not soup:
        print("ERROR: Failed to fetch HTML")
        return

    print("SUCCESS: HTML fetched")

    # Save HTML for inspection
    with open('debug/race_details_html.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("HTML saved to: debug/race_details_html.html")

    # Check for key elements
    print("\n2. Checking for key elements...")

    # Race name
    race_name_elem = soup.select_one('.RaceName')
    print(f"   .RaceName: {'FOUND' if race_name_elem else 'NOT FOUND'}")
    if race_name_elem:
        print(f"   Text: {race_name_elem.get_text(strip=True)}")

    # Race data
    race_data_elem = soup.select_one('.RaceData01')
    print(f"   .RaceData01: {'FOUND' if race_data_elem else 'NOT FOUND'}")
    if race_data_elem:
        print(f"   Text: {race_data_elem.get_text(strip=True)}")

    # Horse list
    horse_list = soup.select('.HorseList')
    print(f"   .HorseList: {len(horse_list)} element(s) found")

    horse_rows = soup.select('.HorseList tr')
    print(f"   .HorseList tr: {len(horse_rows)} rows found")

    # Check first few rows for structure
    print("\n3. Inspecting first 3 horse rows...")
    for i, row in enumerate(horse_rows[:3]):
        print(f"\n   Row {i}:")

        # Check for header
        if row.find('th'):
            print("     This is a HEADER row")
            continue

        # Frame and horse number
        frame_elem = row.select_one('.Waku')
        horse_num_elem = row.select_one('.Umaban')
        print(f"     .Waku: {'FOUND' if frame_elem else 'NOT FOUND'}")
        print(f"     .Umaban: {'FOUND' if horse_num_elem else 'NOT FOUND'}")

        if frame_elem:
            print(f"     Frame number: {frame_elem.get_text(strip=True)}")
        if horse_num_elem:
            print(f"     Horse number: {horse_num_elem.get_text(strip=True)}")

        # Horse info
        horse_link = row.select_one('.Horse_Info a')
        print(f"     .Horse_Info a: {'FOUND' if horse_link else 'NOT FOUND'}")
        if horse_link:
            print(f"     Horse name: {horse_link.get_text(strip=True)}")
            print(f"     Horse href: {horse_link.get('href', '')}")

        # Jockey info
        jockey_link = row.select_one('.Jockey a')
        print(f"     .Jockey a: {'FOUND' if jockey_link else 'NOT FOUND'}")
        if jockey_link:
            print(f"     Jockey name: {jockey_link.get_text(strip=True)}")
            print(f"     Jockey href: {jockey_link.get('href', '')}")

    # Now test the actual function
    print("\n" + "=" * 80)
    print("4. Testing fetch_race_details function...")
    print("=" * 80)

    result = scraper.fetch_race_details(race_id)

    if result:
        print("\nRESULT:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY:")
        print(f"  Race ID: {result.get('race_id')}")
        print(f"  Race Name: {result.get('race_name')}")
        print(f"  Distance: {result.get('distance')}")
        print(f"  Track Type: {result.get('track_type')}")
        print(f"  Number of horses: {len(result.get('horses', []))}")

        if result.get('horses'):
            print(f"\n  First horse:")
            first_horse = result['horses'][0]
            for key, value in first_horse.items():
                print(f"    {key}: {value}")
    else:
        print("ERROR: fetch_race_details returned None")

    print("\n" + "=" * 80)
    print("Test completed")

if __name__ == "__main__":
    main()
