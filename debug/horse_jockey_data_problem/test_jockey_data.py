"""
Debug script to test jockey data fetching
"""
import sys
sys.path.append('/Users/kai/programing/keiba_kaisetsu')

from scraper.jockey import JockeyScraper

def test_jockey_data():
    """Test jockey data fetching"""
    scraper = JockeyScraper()

    # Test with a jockey from the race data: ルメール (05339)
    jockey_id = "05339"

    print(f"Testing jockey data for ID: {jockey_id}")
    print("=" * 60)

    # Fetch jockey stats
    print("\n1. Testing fetch_jockey_stats()...")
    jockey_stats = scraper.fetch_jockey_stats(jockey_id)
    if jockey_stats:
        print(f"✓ Jockey name: {jockey_stats.get('jockey_name', 'N/A')}")
        print(f"✓ Jockey ID: {jockey_stats.get('jockey_id', 'N/A')}")
        print("\n Overall stats:")
        print(f"  {jockey_stats.get('overall_stats', {})}")
        print("\n Recent 5-year stats:")
        print(f"  {jockey_stats.get('recent_5year_stats', {})}")

        # Try to access the way app.py does it (incorrectly)
        print("\n❌ Incorrect access (app.py current implementation):")
        print(f"  win_rate: {jockey_stats.get('win_rate', 0)}")
        print(f"  place_rate: {jockey_stats.get('place_rate', 0)}")

        # Show correct access
        print("\n✓ Correct access:")
        overall = jockey_stats.get('overall_stats', {})
        print(f"  overall win_rate: {overall.get('win_rate', 0)}")
        print(f"  overall place_rate: {overall.get('place_rate', 0)}")
    else:
        print("✗ Failed to fetch jockey stats")

if __name__ == "__main__":
    test_jockey_data()
