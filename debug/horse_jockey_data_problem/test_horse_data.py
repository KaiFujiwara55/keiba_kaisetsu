"""
Debug script to test horse data fetching
"""
import sys
sys.path.append('/Users/kai/programing/keiba_kaisetsu')

from scraper.horse import HorseScraper

def test_horse_data():
    """Test horse data fetching"""
    scraper = HorseScraper()

    # Test with a horse from the race data: サイモフェーン (2023103793)
    horse_id = "2023103793"

    print(f"Testing horse data for ID: {horse_id}")
    print("=" * 60)

    # Fetch horse results
    print("\n1. Testing fetch_horse_results()...")
    horse_results = scraper.fetch_horse_results(horse_id)
    if horse_results:
        print(f"✓ Horse name: {horse_results.get('horse_name', 'N/A')}")
        print(f"✓ Recent results count: {len(horse_results.get('recent_results', []))}")
        print(f"✓ Days since last race: {horse_results.get('days_since_last_race', 'N/A')}")

        if horse_results.get('recent_results'):
            print("\nFirst recent result:")
            print(horse_results['recent_results'][0])
    else:
        print("✗ Failed to fetch horse results")

    # Fetch parent horses
    print("\n2. Testing fetch_parent_horses()...")
    parent_horses = scraper.fetch_parent_horses(horse_id)
    if parent_horses:
        print(f"✓ Sire: {parent_horses.get('sire', {})}")
        print(f"✓ Dam: {parent_horses.get('dam', {})}")
    else:
        print("✗ Failed to fetch parent horses")

    # Fetch overall stats
    print("\n3. Testing fetch_overall_stats()...")
    overall_stats = scraper.fetch_overall_stats(horse_id)
    if overall_stats:
        print(f"✓ Horse name: {overall_stats.get('horse_name', 'N/A')}")
        print(f"✓ Overall record: {overall_stats.get('overall_record', 'N/A')}")
        print(f"✓ Wins: {overall_stats.get('wins', 'N/A')}")
        print(f"✓ Races: {overall_stats.get('races', 'N/A')}")
    else:
        print("✗ Failed to fetch overall stats")

if __name__ == "__main__":
    test_horse_data()
