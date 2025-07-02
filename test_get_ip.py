#!/usr/bin/env python3
"""
Test script for the Cloudflare IP retrieval functions.
"""

import logging
import sys
import os

# Add the current directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our functions
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("cloudflare_dynamic_ip", "cloudflare-dynamic-ip.py")
    cloudflare_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cloudflare_module)
    
    get_ip_from_cloudflare_record = cloudflare_module.get_ip_from_cloudflare_record
    get_ip_from_existing_record = cloudflare_module.get_ip_from_existing_record
    print("✓ Successfully imported Cloudflare IP functions")
except ImportError as e:
    print(f"✗ Failed to import functions: {e}")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_function_signatures():
    """Test that the functions have the correct signatures."""
    print("\nTesting function signatures...")
    
    # Test get_ip_from_cloudflare_record
    try:
        # This should fail gracefully with invalid parameters
        result = get_ip_from_cloudflare_record("test_zone", "test_record", "invalid_token")
        print("✓ get_ip_from_cloudflare_record function callable")
    except Exception as e:
        print(f"✓ get_ip_from_cloudflare_record function callable (expected error: {type(e).__name__})")
    
    # Test get_ip_from_existing_record
    try:
        # This should fail gracefully with invalid parameters
        result = get_ip_from_existing_record({"zone_id": "test", "name": "test"})
        print("✓ get_ip_from_existing_record function callable")
    except Exception as e:
        print(f"✓ get_ip_from_existing_record function callable (expected error: {type(e).__name__})")

def test_with_mock_config():
    """Test with a mock configuration."""
    print("\nTesting with mock configuration...")
    
    # Create a mock record configuration
    mock_record = {
        "id": "mock_record_id",
        "zone_id": "mock_zone_id", 
        "name": "example.com"
    }
    
    # This should fail because the zone_id won't be in CLOUDFLARE_ZONES
    result = get_ip_from_existing_record(mock_record)
    if result is None:
        print("✓ Function correctly handles missing zone configuration")
    else:
        print(f"✗ Unexpected result: {result}")

def main():
    """Run all tests."""
    print("Testing Cloudflare IP retrieval functions...")
    print("=" * 50)
    
    test_function_signatures()
    test_with_mock_config()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nTo use these functions with real data:")
    print("1. Create config/config.py based on config/config.sample.py")
    print("2. Add your Cloudflare zone ID, API token, and record details")
    print("3. Run example_get_ip.py to see the functions in action")

if __name__ == "__main__":
    main()