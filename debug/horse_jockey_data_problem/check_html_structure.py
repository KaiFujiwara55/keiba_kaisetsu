"""
Check the HTML structure of horse results table
"""
import sys
sys.path.append('/Users/kai/programing/keiba_kaisetsu')

from scraper.horse import HorseScraper

def check_html_structure():
    """Check HTML structure of results table"""
    scraper = HorseScraper()

    horse_id = "2023103793"
    url = f"{scraper.BASE_URL}/horse/result/{horse_id}/"

    print(f"Fetching URL: {url}")
    print("=" * 70)

    soup = scraper.fetch(url)
    if not soup:
        print("✗ Failed to fetch page")
        return

    results_table = soup.select_one('.db_h_race_results')
    if not results_table:
        print("✗ Results table not found")
        return

    print("✓ Found results table\n")

    # Check table headers to understand column structure
    headers = results_table.select('thead th')
    print(f"Number of header columns: {len(headers)}")
    print("\nHeader columns:")
    for i, header in enumerate(headers):
        header_text = header.get_text(strip=True)
        print(f"  Column {i}: {header_text}")

    # Check first data row
    result_rows = results_table.select('tbody tr')
    if result_rows:
        print(f"\nNumber of data rows: {len(result_rows)}")
        print("\nFirst row cells:")

        first_row = result_rows[0]
        cells = first_row.select('td')

        print(f"Number of cells: {len(cells)}")
        for i, cell in enumerate(cells[:15]):  # Show first 15 cells
            cell_text = cell.get_text(strip=True)
            print(f"  Cell {i} (td:nth-of-type({i+1})): {cell_text}")

if __name__ == "__main__":
    check_html_structure()
