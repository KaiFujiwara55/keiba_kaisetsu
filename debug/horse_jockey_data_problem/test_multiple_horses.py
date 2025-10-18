"""
Debug script to test multiple horses with different experience levels
"""
import sys
sys.path.append('/Users/kai/programing/keiba_kaisetsu')

from scraper.horse import HorseScraper

def test_multiple_horses():
    """Test horse data fetching for different horses"""
    scraper = HorseScraper()

    # Test horses:
    # 1. New horse with minimal results (from race data)
    # 2. Experienced horse with many results
    test_horses = [
        ("2023103793", "サイモフェーン (new horse)"),
        ("2021101742", "ヴァントクール (more experienced)"),  # Random experienced horse ID
    ]

    for horse_id, description in test_horses:
        print(f"\nTesting: {description} (ID: {horse_id})")
        print("=" * 60)

        url = f"{scraper.BASE_URL}/horse/{horse_id}/"
        soup = scraper.fetch(url)

        if not soup:
            print("✗ Failed to fetch page")
            continue

        # Check for results table
        results_table = soup.select_one('.db_h_race_results')
        if results_table:
            result_rows = results_table.select('tbody tr')
            print(f"✓ Found .db_h_race_results table with {len(result_rows)} rows")
        else:
            print("✗ .db_h_race_results table not found")

            # Try alternative URL: /horse/result/{horse_id}/
            print(f"\nTrying alternative URL: {scraper.BASE_URL}/horse/result/{horse_id}/")
            alt_url = f"{scraper.BASE_URL}/horse/result/{horse_id}/"
            alt_soup = scraper.fetch(alt_url)

            if alt_soup:
                alt_results_table = alt_soup.select_one('.db_h_race_results')
                if alt_results_table:
                    alt_result_rows = alt_results_table.select('tbody tr')
                    print(f"✓ Found .db_h_race_results table at alternative URL with {len(alt_result_rows)} rows")
                else:
                    print("✗ .db_h_race_results table not found at alternative URL either")
            else:
                print("✗ Failed to fetch alternative URL")

if __name__ == "__main__":
    test_multiple_horses()
