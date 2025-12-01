#!/usr/bin/env python3
"""Test script for offer_id number extraction and sorting."""
from src.utils import extract_offer_id_number

# Test cases
test_cases = [
    ("р20-п5-33", 20),
    ("р25-п5-33", 25),
    ("р30-п5-33", 30),
    ("мд33-п2-30", 33),
    ("р1-п5-33", 1),
    ("р99-п5-33", 99),
    ("р100-п5-33", None),  # Over 99
    ("р0-п5-33", None),    # Under 1
    ("invalid", None),
    ("р5", 5),
    ("мд10-п2", 10),
]

print("Testing extract_offer_id_number function:")
print("=" * 60)

all_passed = True
for offer_id, expected in test_cases:
    result = extract_offer_id_number(offer_id)
    status = "✅" if result == expected else "❌"
    if result != expected:
        all_passed = False
    print(f"{status} '{offer_id}' -> {result} (expected {expected})")

print("=" * 60)
if all_passed:
    print("✅ All tests passed!")
else:
    print("❌ Some tests failed!")

# Test sorting
print("\nTesting sorting:")
print("=" * 60)
test_products = [
    {"offer_id": "р30-п5-33", "name": "Product 30"},
    {"offer_id": "р5-п5-33", "name": "Product 5"},
    {"offer_id": "р20-п5-33", "name": "Product 20"},
    {"offer_id": "мд33-п2-30", "name": "Product 33"},
    {"offer_id": "р1-п5-33", "name": "Product 1"},
    {"offer_id": "р25-п5-33", "name": "Product 25"},
]

# Filter and sort
filtered = []
for product in test_products:
    number = extract_offer_id_number(product["offer_id"])
    if number is not None:
        product["_sort_number"] = number
        filtered.append(product)

filtered.sort(key=lambda x: x.get("_sort_number", 999))

print("Sorted products:")
for product in filtered:
    num = product.pop("_sort_number", None)
    print(f"  {num}: {product['offer_id']} - {product['name']}")

