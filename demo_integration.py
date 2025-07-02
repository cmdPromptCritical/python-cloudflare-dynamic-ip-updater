#!/usr/bin/env python3
"""
Demonstration of how to integrate the new IP retrieval functions 
with the existing dynamic IP update workflow.
"""

import logging
import importlib.util

# Import functions from the main module
spec = importlib.util.spec_from_file_location("cloudflare_dynamic_ip", "cloudflare-dynamic-ip.py")
cloudflare_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cloudflare_module)

get_ip_from_cloudflare_record = cloudflare_module.get_ip_from_cloudflare_record
get_ip_from_existing_record = cloudflare_module.get_ip_from_existing_record
get_current_ip = cloudflare_module.get_current_ip

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def demo_ip_comparison():
    """
    Demonstrate comparing current external IP with DNS record IP.
    """
    print("=== IP Comparison Demo ===")
    
    # Get current external IP (existing functionality)
    try:
        current_external_ip = get_current_ip().strip()
        print(f"Current external IP: {current_external_ip}")
    except Exception as e:
        print(f"Failed to get current external IP: {e}")
        return
    
    # Example: Get IP from DNS record (would need real credentials)
    print("\nTo compare with DNS record IP, you would:")
    print("1. Configure your Cloudflare credentials in config/config.py")
    print("2. Use get_ip_from_cloudflare_record() or get_ip_from_existing_record()")
    print("3. Compare the IPs to determine if an update is needed")
    
    # Simulated comparison
    print(f"\nExample comparison logic:")
    print(f"if current_external_ip != dns_record_ip:")
    print(f"    print('Update needed: {current_external_ip} != dns_record_ip')")
    print(f"    # Proceed with update using existing update_record() function")
    print(f"else:")
    print(f"    print('No update needed - IPs match')")

def demo_enhanced_workflow():
    """
    Demonstrate an enhanced workflow that checks DNS records before updating.
    """
    print("\n=== Enhanced Workflow Demo ===")
    
    print("Enhanced workflow steps:")
    print("1. Get current external IP")
    print("2. Get current DNS record IP")
    print("3. Compare IPs")
    print("4. Only update if different")
    print("5. Verify update by checking DNS record again")
    
    print("\nBenefits of this approach:")
    print("- Avoid unnecessary API calls when IP hasn't changed")
    print("- Verify updates were successful")
    print("- Better logging and monitoring")
    print("- Reduced API rate limit usage")

def demo_multiple_records():
    """
    Demonstrate handling multiple DNS records.
    """
    print("\n=== Multiple Records Demo ===")
    
    print("For multiple DNS records, you can:")
    print("1. Check each record individually")
    print("2. Update only records that need updating")
    print("3. Verify each update")
    
    print("\nExample code structure:")
    print("""
from config.config import CLOUDFLARE_RECORDS

current_ip = get_current_ip().strip()

for record in CLOUDFLARE_RECORDS:
    dns_ip = get_ip_from_existing_record(record)
    
    if dns_ip != current_ip:
        print(f"Updating {record['name']}: {dns_ip} -> {current_ip}")
        # Use existing update_record() function
        success = update_record(record, current_ip)
        
        if success:
            # Verify the update
            new_ip = get_ip_from_existing_record(record)
            if new_ip == current_ip:
                print(f"✓ Update verified for {record['name']}")
            else:
                print(f"✗ Update verification failed for {record['name']}")
    else:
        print(f"No update needed for {record['name']}")
""")

def main():
    """Run all demonstrations."""
    print("Cloudflare DNS IP Retrieval - Integration Demo")
    print("=" * 60)
    
    demo_ip_comparison()
    demo_enhanced_workflow()
    demo_multiple_records()
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("\nTo use these features with real data:")
    print("1. Set up your Cloudflare credentials in config/config.py")
    print("2. Test with example_get_ip.py")
    print("3. Integrate into your existing workflow")

if __name__ == "__main__":
    main()