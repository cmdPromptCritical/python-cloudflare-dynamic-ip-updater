#!/usr/bin/env python3
"""
Example script demonstrating how to get current IP from Cloudflare DNS records.
"""

import logging
import importlib.util

# Import functions from the main module
spec = importlib.util.spec_from_file_location("cloudflare_dynamic_ip", "cloudflare-dynamic-ip.py")
cloudflare_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cloudflare_module)

get_ip_from_cloudflare_record = cloudflare_module.get_ip_from_cloudflare_record
get_ip_from_existing_record = cloudflare_module.get_ip_from_existing_record

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def example_usage():
    """
    Example usage of the Cloudflare IP retrieval functions.
    """
    
    # Example 1: Get IP directly with parameters
    print("Example 1: Get IP directly with zone_id, record_name, and api_token")
    zone_id = "your_zone_id_here"
    record_name = "example.com"  # or subdomain.example.com
    api_token = "your_api_token_here"
    
    ip = get_ip_from_cloudflare_record(zone_id, record_name, api_token)
    if ip:
        print(f"Current IP for {record_name}: {ip}")
    else:
        print(f"Failed to retrieve IP for {record_name}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Get IP using existing configuration format
    print("Example 2: Get IP using existing record configuration")
    
    # This would use the configuration from config/config.py
    # Make sure you have a proper config.py file based on config.sample.py
    try:
        from config.config import CLOUDFLARE_RECORDS
        
        if CLOUDFLARE_RECORDS:
            # Get IP from the first configured record
            record_config = CLOUDFLARE_RECORDS[0]
            ip = get_ip_from_existing_record(record_config)
            
            if ip:
                print(f"Current IP for {record_config['name']}: {ip}")
            else:
                print(f"Failed to retrieve IP for {record_config['name']}")
        else:
            print("No records configured in CLOUDFLARE_RECORDS")
            
    except ImportError:
        print("Config file not found. Please create config/config.py based on config/config.sample.py")
    except Exception as e:
        print(f"Error reading configuration: {e}")

if __name__ == "__main__":
    example_usage()