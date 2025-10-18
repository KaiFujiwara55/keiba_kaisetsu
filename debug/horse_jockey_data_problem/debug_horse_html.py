"""
Debug script to check horse page HTML structure
"""
import sys
sys.path.append('/Users/kai/programing/keiba_kaisetsu')

from scraper.horse import HorseScraper

def debug_horse_html():
    """Check horse HTML structure"""
    scraper = HorseScraper()

    # Test with a horse from the race data: サイモフェーン (2023103793)
    horse_id = "2023103793"

    url = f"{scraper.BASE_URL}/horse/{horse_id}/"
    print(f"Fetching URL: {url}")
    print("=" * 60)

    soup = scraper.fetch(url)
    if not soup:
        print("Failed to fetch page")
        return

    # Check for results table
    print("\n1. Checking for .db_h_race_results table...")
    results_table = soup.select_one('.db_h_race_results')
    if results_table:
        print("✓ Found .db_h_race_results table")

        # Count rows
        result_rows = results_table.select('tbody tr')
        print(f"✓ Found {len(result_rows)} rows in tbody")

        # Show first row HTML
        if result_rows:
            print("\nFirst row HTML:")
            print(result_rows[0].prettify()[:500])

            # Try to extract data from first row
            row = result_rows[0]
            print("\nExtracting data from first row:")
            print(f"  Date (td:nth-of-type(1)): {scraper.safe_extract_text(row, 'td:nth-of-type(1)', 'N/A')}")
            print(f"  Track (td:nth-of-type(2) a): {scraper.safe_extract_text(row, 'td:nth-of-type(2) a', 'N/A')}")
            print(f"  Distance (td:nth-of-type(3)): {scraper.safe_extract_text(row, 'td:nth-of-type(3)', 'N/A')}")
            print(f"  Position (td:nth-of-type(4)): {scraper.safe_extract_text(row, 'td:nth-of-type(4)', 'N/A')}")
    else:
        print("✗ .db_h_race_results table not found")

        # Look for alternative table
        print("\nSearching for alternative table structures...")
        all_tables = soup.find_all('table')
        print(f"Found {len(all_tables)} table(s) on page")

        for i, table in enumerate(all_tables):
            class_names = table.get('class', [])
            print(f"  Table {i + 1}: classes = {class_names}")

    # Check profile table for overall stats
    print("\n2. Checking for .db_prof_table (profile)...")
    profile_table = soup.select_one('.db_prof_table')
    if profile_table:
        print("✓ Found .db_prof_table")

        rows = profile_table.select('tr')
        for row in rows:
            th = row.select_one('th')
            td = row.select_one('td')
            if th and td:
                header = th.get_text(strip=True)
                if '通算成績' in header:
                    overall_record = td.get_text(strip=True)
                    print(f"✓ Overall record: {overall_record}")
    else:
        print("✗ .db_prof_table not found")

if __name__ == "__main__":
    debug_horse_html()
