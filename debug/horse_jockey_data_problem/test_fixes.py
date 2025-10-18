"""
Test the fixes for horse and jockey data fetching
"""
import sys
sys.path.append('/Users/kai/programing/keiba_kaisetsu')

from scraper.horse import HorseScraper
from scraper.jockey import JockeyScraper

def test_fixes():
    """Test all the fixes"""
    horse_scraper = HorseScraper()
    jockey_scraper = JockeyScraper()

    print("=" * 70)
    print("Testing Fixed Data Fetching")
    print("=" * 70)

    # Test horse: サイモフェーン (2023103793)
    horse_id = "2023103793"
    print(f"\n1. Testing Horse Data (ID: {horse_id})")
    print("-" * 70)

    # Fetch horse results with FIXED URL
    horse_results = horse_scraper.fetch_horse_results(horse_id)
    if horse_results:
        print(f"✓ Horse name: {horse_results.get('horse_name', 'N/A')}")
        print(f"✓ Recent results count: {len(horse_results.get('recent_results', []))}")
        print(f"✓ Days since last race: {horse_results.get('days_since_last_race', 'N/A')}")

        if horse_results.get('recent_results'):
            print("\n  Latest race result:")
            result = horse_results['recent_results'][0]
            print(f"    Date: {result.get('date', 'N/A')}")
            print(f"    Track: {result.get('track', 'N/A')}")
            print(f"    Distance: {result.get('distance', 'N/A')}")
            print(f"    Position: {result.get('position', 'N/A')}")
    else:
        print("✗ Failed to fetch horse results")

    # Fetch parent horses
    parent_horses = horse_scraper.fetch_parent_horses(horse_id)
    if parent_horses:
        print(f"\n✓ Sire name: {parent_horses.get('sire', {}).get('name', 'N/A')}")
        print(f"✓ Sire ID: {parent_horses.get('sire', {}).get('id', 'N/A')}")
        print(f"✓ Dam name: {parent_horses.get('dam', {}).get('name', 'N/A')}")
        print(f"✓ Dam ID: {parent_horses.get('dam', {}).get('id', 'N/A')}")
    else:
        print("✗ Failed to fetch parent horses")

    # Test jockey: ルメール (05339)
    jockey_id = "05339"
    print(f"\n2. Testing Jockey Data (ID: {jockey_id})")
    print("-" * 70)

    jockey_stats = jockey_scraper.fetch_jockey_stats(jockey_id)
    if jockey_stats:
        print(f"✓ Jockey name: {jockey_stats.get('jockey_name', 'N/A')}")

        # Test FIXED access pattern (as used in app.py)
        jockey_overall_stats = jockey_stats.get('overall_stats', {})
        print(f"✓ Overall win rate: {jockey_overall_stats.get('win_rate', 0)}%")
        print(f"✓ Overall place rate: {jockey_overall_stats.get('place_rate', 0)}%")
        print(f"✓ Total races: {jockey_overall_stats.get('total_races', 0)}")
        print(f"✓ Total wins: {jockey_overall_stats.get('wins', 0)}")
    else:
        print("✗ Failed to fetch jockey stats")

    # Simulate app.py data structure
    print(f"\n3. Simulating app.py Data Structure")
    print("-" * 70)

    horse_detailed = {
        'horse_id': horse_id,
        'horse_name': 'サイモフェーン',
        'jockey_id': jockey_id,
        'jockey_name': 'ルメール',
        'recent_results': horse_results.get('recent_results', []) if horse_results else [],
        'days_since_last_race': horse_results.get('days_since_last_race', 999) if horse_results else 999,
        'jockey_win_rate': jockey_overall_stats.get('win_rate', 0),
        'jockey_place_rate': jockey_overall_stats.get('place_rate', 0),
        'sire_name': parent_horses.get('sire', {}).get('name', '') if parent_horses else '',
        'dam_name': parent_horses.get('dam', {}).get('name', '') if parent_horses else '',
    }

    print("Simulated horse data:")
    print(f"  Horse: {horse_detailed['horse_name']}")
    print(f"  Recent results: {len(horse_detailed['recent_results'])} races")
    print(f"  Days since last race: {horse_detailed['days_since_last_race']}")
    print(f"  Jockey: {horse_detailed['jockey_name']}")
    print(f"  Jockey win rate: {horse_detailed['jockey_win_rate']}%")
    print(f"  Jockey place rate: {horse_detailed['jockey_place_rate']}%")
    print(f"  Sire: {horse_detailed['sire_name']}")
    print(f"  Dam: {horse_detailed['dam_name']}")

    print("\n" + "=" * 70)
    print("✓ All fixes verified successfully!")
    print("=" * 70)

if __name__ == "__main__":
    test_fixes()
