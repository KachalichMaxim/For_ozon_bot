#!/usr/bin/env python3
"""Test script to verify Ozon API connection and order fetching."""
import sys
from datetime import datetime, timedelta
from src.ozon_client import OzonClient

# Test credentials
CLIENT_ID = "2585490"
API_KEY = "4679a7b8-b2be-41d7-af42-7ccb0e6a932e"


def main():
    """Test Ozon API connection and fetch orders."""
    print("=" * 60)
    print("Testing Ozon API Connection")
    print("=" * 60)
    print(f"Client ID: {CLIENT_ID}")
    print(f"API Key: {API_KEY[:20]}...")
    print()
    
    # Initialize client
    try:
        client = OzonClient(client_id=CLIENT_ID, api_key=API_KEY)
        print("✅ Ozon client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        sys.exit(1)
    
    # Calculate expected date range
    cutoff_from = (datetime.utcnow() - timedelta(days=30)).strftime(
        "%Y-%m-%dT%H:%M:%S.000Z"
    )
    print(f"\n📅 Date range: from {cutoff_from} to now (30 days)")
    print()
    
    # Test 1: Fetch first page
    print("Test 1: Fetching first page of postings...")
    try:
        response = client.get_postings(limit=1000)
        postings = response.get("postings", [])
        cursor = response.get("cursor", "")
        
        print(f"✅ Successfully fetched {len(postings)} postings")
        print(f"   Cursor: {cursor[:50] if cursor else 'None'}...")
        
        if postings:
            print(f"\n   First posting number: {postings[0].get('posting_number', 'N/A')}")
            print(f"   First posting products: {len(postings[0].get('products', []))}")
        
    except Exception as e:
        print(f"❌ Failed to fetch postings: {e}")
        sys.exit(1)
    
    # Test 2: Fetch all postings with pagination
    print("\n" + "=" * 60)
    print("Test 2: Fetching ALL postings (with pagination)...")
    print("=" * 60)
    
    try:
        all_postings = client.get_all_postings()
        print(f"\n✅ Successfully fetched {len(all_postings)} total postings")
        
        if all_postings:
            # Count products
            total_products = 0
            posting_numbers = []
            for posting in all_postings:
                products = posting.get("products", [])
                total_products += len(products)
                posting_numbers.append(posting.get("posting_number", ""))
            
            print(f"   Total products: {total_products}")
            print(f"   Posting numbers: {', '.join(posting_numbers[:10])}")
            if len(posting_numbers) > 10:
                print(f"   ... and {len(posting_numbers) - 10} more")
        else:
            print("   ⚠️  No postings found in the last 30 days")
            
    except Exception as e:
        print(f"❌ Failed to fetch all postings: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

