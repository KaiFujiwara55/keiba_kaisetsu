"""
Check the structure of recent_results to identify the time field issue
"""
import sys
sys.path.append('/Users/kai/programing/keiba_kaisetsu')

from scraper.horse import HorseScraper
import json

def check_recent_results():
    """Check recent_results structure in detail"""
    scraper = HorseScraper()

    # Test with a horse that has some race history
    horse_id = "2023103793"

    print(f"Checking recent_results for horse ID: {horse_id}")
    print("=" * 70)

    horse_results = scraper.fetch_horse_results(horse_id)

    if not horse_results:
        print("✗ Failed to fetch horse results")
        return

    print(f"Horse name: {horse_results.get('horse_name', 'N/A')}")
    print(f"Number of recent results: {len(horse_results.get('recent_results', []))}")

    if horse_results.get('recent_results'):
        print("\nRecent results structure:")
        for i, result in enumerate(horse_results['recent_results']):
            print(f"\nResult {i + 1}:")
            print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    check_recent_results()
