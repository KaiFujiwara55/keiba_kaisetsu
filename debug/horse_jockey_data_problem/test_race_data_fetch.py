"""
Test race data fetching with the fixes applied
This simulates the fetch_race_data_with_cache function
"""
import sys
sys.path.append('/Users/kai/programing/keiba_kaisetsu')

from scraper.race import RaceScraper
from scraper.horse import HorseScraper
from scraper.jockey import JockeyScraper

def test_race_data_fetch(race_id: str):
    """
    Test complete race data fetching

    Args:
        race_id: Race identifier
    """
    race_scraper = RaceScraper()
    horse_scraper = HorseScraper()
    jockey_scraper = JockeyScraper()

    print(f"Fetching race data for race ID: {race_id}")
    print("=" * 70)

    # Fetch race details
    print("\n1. Fetching race metadata...")
    race_data = race_scraper.fetch_race_details(race_id)

    if not race_data:
        print("✗ Failed to fetch race data")
        return None

    print(f"✓ Race: {race_data['race_name']}")
    print(f"✓ Distance: {race_data['distance']}")
    print(f"✓ Track type: {race_data['track_type']}")
    print(f"✓ Number of horses: {len(race_data['horses'])}")

    # Fetch detailed data for each horse (limit to first 3 for speed)
    print("\n2. Fetching detailed horse data (first 3 horses)...")
    horses_detailed = []

    for idx, horse in enumerate(race_data['horses'][:3]):
        horse_id = horse['horse_id']
        jockey_id = horse['jockey_id']

        print(f"\n  Horse {idx + 1}: {horse['horse_name']} (Jockey: {horse['jockey_name']})")

        # Fetch horse results
        horse_results = horse_scraper.fetch_horse_results(horse_id)
        if horse_results:
            print(f"    ✓ Recent results: {len(horse_results.get('recent_results', []))} races")
            print(f"    ✓ Days since last race: {horse_results.get('days_since_last_race', 999)}")
        else:
            print(f"    ✗ Failed to fetch horse results")

        # Fetch parent horses
        parent_horses = horse_scraper.fetch_parent_horses(horse_id)
        if parent_horses:
            print(f"    ✓ Sire: {parent_horses.get('sire', {}).get('name', 'N/A')}")
            print(f"    ✓ Dam: {parent_horses.get('dam', {}).get('name', 'N/A')}")
        else:
            print(f"    ✗ Failed to fetch parent horses")

        # Fetch jockey stats
        jockey_stats = jockey_scraper.fetch_jockey_stats(jockey_id)
        if jockey_stats:
            jockey_overall_stats = jockey_stats.get('overall_stats', {})
            print(f"    ✓ Jockey win rate: {jockey_overall_stats.get('win_rate', 0)}%")
            print(f"    ✓ Jockey place rate: {jockey_overall_stats.get('place_rate', 0)}%")
        else:
            print(f"    ✗ Failed to fetch jockey stats")

        # Combine all data (as in app.py)
        jockey_overall_stats = jockey_stats.get('overall_stats', {}) if jockey_stats else {}

        horse_detailed = {
            **horse,
            'recent_results': horse_results.get('recent_results', []) if horse_results else [],
            'days_since_last_race': horse_results.get('days_since_last_race', 999) if horse_results else 999,
            'jockey_win_rate': jockey_overall_stats.get('win_rate', 0),
            'jockey_place_rate': jockey_overall_stats.get('place_rate', 0),
            'sire_name': parent_horses.get('sire', {}).get('name', '') if parent_horses else '',
            'dam_name': parent_horses.get('dam', {}).get('name', '') if parent_horses else '',
        }

        horses_detailed.append(horse_detailed)

    # Display summary
    print("\n" + "=" * 70)
    print("Summary of first 3 horses:")
    print("=" * 70)

    for horse in horses_detailed:
        print(f"\n{horse['horse_name']} (Jockey: {horse['jockey_name']})")
        print(f"  Recent results: {len(horse['recent_results'])} races")
        print(f"  Days since last race: {horse['days_since_last_race']}")
        print(f"  Jockey win rate: {horse['jockey_win_rate']}%")
        print(f"  Jockey place rate: {horse['jockey_place_rate']}%")
        print(f"  Sire: {horse['sire_name']}")
        print(f"  Dam: {horse['dam_name']}")

    print("\n" + "=" * 70)
    print("✓ Race data fetching test completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    # Test with the race ID from the user's output
    race_id = "202505040601"
    test_race_data_fetch(race_id)
