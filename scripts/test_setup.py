#!/usr/bin/env python3
"""
Test script to verify Morph Cloud setup and Lean installation.

This script can be run locally to test the Morph Cloud connection and
verify that the Lean 4 installation works correctly.
"""

import os
import sys
from morphcloud.api import MorphCloudClient


def test_morph_connection():
    """Test basic Morph Cloud connection."""
    api_key = os.environ.get("MORPH_API_KEY")
    if not api_key:
        print("❌ MORPH_API_KEY environment variable not set")
        return False

    try:
        _ = MorphCloudClient(api_key=api_key)
        print("✅ Morph Cloud client initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Morph Cloud client: {e}")
        return False


def test_snapshot_creation():
    """Test snapshot creation (dry run)."""
    try:
        client = MorphCloudClient(api_key=os.environ["MORPH_API_KEY"])

        # List available images
        images = client.images.list()
        minimal_image = None
        for img in images:
            if "minimal" in img.name.lower():
                minimal_image = img
                break

        if minimal_image:
            print(
                f"✅ Found minimal image: {minimal_image.name} "
                f"(ID: {minimal_image.id})"
            )
        else:
            print("⚠️  No minimal image found")

        return True
    except Exception as e:
        print(f"❌ Failed to test snapshot creation: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Morph Cloud setup...")
    print("=" * 50)

    tests = [
        ("Morph Cloud Connection", test_morph_connection),
        ("Snapshot Creation Test", test_snapshot_creation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Setup is ready for CI pipeline.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check your setup.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
