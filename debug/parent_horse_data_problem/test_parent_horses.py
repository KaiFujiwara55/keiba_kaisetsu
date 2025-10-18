#!/usr/bin/env python3
"""
Debug script to test parent horse data fetching
Tests the modified fetch_parent_horses method to ensure it properly fetches
earnings and record for both sire and dam.
"""

import sys
import os
import json

# Add parent directory to path to import scraper
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scraper.horse import HorseScraper


def test_parent_horses(horse_id: str):
    """
    Test fetching parent horse information including earnings and record

    Args:
        horse_id: ID of the horse to test
    """
    print(f"Testing parent horse data for horse ID: {horse_id}")
    print("=" * 60)

    scraper = HorseScraper()

    # Fetch parent horses
    print("\nFetching parent horses...")
    parent_data = scraper.fetch_parent_horses(horse_id)

    if not parent_data:
        print("ERROR: Failed to fetch parent horse data")
        return False

    print("\nParent Horse Data:")
    print(json.dumps(parent_data, indent=2, ensure_ascii=False))

    # Validate sire data
    print("\n" + "=" * 60)
    print("Validating Sire (父馬) Data:")
    sire = parent_data.get('sire', {})
    print(f"  Name: {sire.get('name', 'MISSING')}")
    print(f"  ID: {sire.get('id', 'MISSING')}")
    print(f"  Earnings: {sire.get('earnings', 'MISSING')}")
    print(f"  1着: {sire.get('first', 'MISSING')}")
    print(f"  2着: {sire.get('second', 'MISSING')}")
    print(f"  3着: {sire.get('third', 'MISSING')}")
    print(f"  4着以降: {sire.get('fourth_or_lower', 'MISSING')}")

    sire_valid = all([
        sire.get('name'),
        sire.get('id'),
        sire.get('earnings'),
        'first' in sire,
        'second' in sire,
        'third' in sire,
        'fourth_or_lower' in sire
    ])

    if sire_valid:
        print("  ✓ Sire data is complete")
    else:
        print("  ✗ Sire data is incomplete")

    # Validate dam data
    print("\nValidating Dam (母馬) Data:")
    dam = parent_data.get('dam', {})
    print(f"  Name: {dam.get('name', 'MISSING')}")
    print(f"  ID: {dam.get('id', 'MISSING')}")
    print(f"  Earnings: {dam.get('earnings', 'MISSING')}")
    print(f"  1着: {dam.get('first', 'MISSING')}")
    print(f"  2着: {dam.get('second', 'MISSING')}")
    print(f"  3着: {dam.get('third', 'MISSING')}")
    print(f"  4着以降: {dam.get('fourth_or_lower', 'MISSING')}")

    dam_valid = all([
        dam.get('name'),
        dam.get('id'),
        dam.get('earnings'),
        'first' in dam,
        'second' in dam,
        'third' in dam,
        'fourth_or_lower' in dam
    ])

    if dam_valid:
        print("  ✓ Dam data is complete")
    else:
        print("  ✗ Dam data is incomplete")

    # Overall result
    print("\n" + "=" * 60)
    if sire_valid and dam_valid:
        print("✓ TEST PASSED: All parent horse data fetched successfully")
        return True
    else:
        print("✗ TEST FAILED: Some parent horse data is missing")
        return False


if __name__ == "__main__":
    # Test with a known horse ID
    # エスポワールシチー (from user selection in test.json)
    test_horse_id = "2017101352"

    # You can override with command line argument
    if len(sys.argv) > 1:
        test_horse_id = sys.argv[1]

    success = test_parent_horses(test_horse_id)
    sys.exit(0 if success else 1)
