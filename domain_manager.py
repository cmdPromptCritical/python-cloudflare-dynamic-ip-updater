#!/usr/bin/env python3
import os
import sys
import json
try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Please install it using:")
    print("pip install requests")
    sys.exit(1)

import pprint

CONFIG_FILE = "config/config.py"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found.")
        sys.exit(1)
    
    config = {}
    try:
        with open(CONFIG_FILE, "r") as f:
            code = f.read()
            # We execute the config file in a local namespace to get its variables
            exec(code, {"logging": __import__("logging")}, config)
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)
    
    # Filter only the upper-case variables (standard config style)
    return {k: v for k, v in config.items() if k.isupper()}

def save_config(config_data):
    # Re-implementing a simple python-style formatter for the data
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write("import logging\n\n")
            
            # Sort keys to keep file somewhat consistent
            for key in sorted(config_data.keys()):
                value = config_data[key]
                
                if key == "LOGGING_LEVEL":
                     # We assume it was logging.INFO or similar. 
                     # To be safe, we'll just write it as logging.INFO 
                     # unless we want to parse the level name.
                     f.write(f"LOGGING_LEVEL = logging.INFO\n\n")
                     continue
                
                # Using pprint for better Python-style formatting
                formatted_value = pprint.pformat(value, indent=4, width=120)
                f.write(f"{key} = {formatted_value}\n\n")
    except Exception as e:
        print(f"Error saving config file: {e}")

def get_cloudflare_record(zone_id, token, subdomain_name):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"type": "A", "name": subdomain_name}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            print(f"Cloudflare API error: {data.get('errors')}")
            return None
            
        results = data.get("result", [])
        if not results:
            print(f"No 'A' record found for {subdomain_name} in zone {zone_id}.")
            return None
            
        return results[0] # Return the first matching record
    except Exception as e:
        print(f"Error connecting to Cloudflare: {e}")
        return None

def list_records(config):
    records = config.get("CLOUDFLARE_RECORDS", [])
    if not records:
        print("\nNo records configured.")
        return
    
    print("\n--- Currently Subscribed Records ---")
    print(f"{'#':<3} {'Name':<30} {'Zone ID':<35} {'Proxied':<8}")
    print("-" * 80)
    for i, rec in enumerate(records):
        print(f"{i:<3} {rec['name']:<30} {rec['zone_id']:<35} {str(rec['proxied']):<8}")

def add_record(config):
    zone_id = input("\nEnter Zone ID: ").strip()
    subdomain_name = input("Enter Subdomain Name (e.g., test.example.com): ").strip()
    proxied_input = input("Should it be proxied by Cloudflare? (y/N): ").strip().lower()
    proxied = proxied_input == 'y'
    
    zones = config.get("CLOUDFLARE_ZONES", {})
    token = ""
    
    if zone_id in zones:
        token = zones[zone_id]["token"]
        print(f"Using existing token for zone: {zones[zone_id]['name']}")
    else:
        print(f"Zone {zone_id} not found in existing config.")
        zone_name = input("Enter Zone Name (domain name, e.g., example.com): ").strip()
        token = input("Enter Cloudflare API Token for this zone: ").strip()
        
        # Add to zones
        zones[zone_id] = {
            "id": zone_id,
            "name": zone_name,
            "token": token
        }
        config["CLOUDFLARE_ZONES"] = zones

    print(f"Fetching record ID for {subdomain_name}...")
    record_data = get_cloudflare_record(zone_id, token, subdomain_name)
    
    if record_data:
        record_id = record_data["id"]
        print(f"Found Record ID: {record_id}")
        
        # Check if already exists
        records = config.get("CLOUDFLARE_RECORDS", [])
        for r in records:
            if r["id"] == record_id:
                print(f"Error: Record {subdomain_name} is already in the list.")
                return

        new_record = {
            "id": record_id,
            "zone_id": zone_id,
            "name": subdomain_name,
            "proxied": proxied
        }
        
        records.append(new_record)
        config["CLOUDFLARE_RECORDS"] = records
        
        save_config(config)
        print(f"Successfully added {subdomain_name}!")
    else:
        print("Failed to add record. Please check the details and try again.")

def remove_record(config):
    records = config.get("CLOUDFLARE_RECORDS", [])
    if not records:
        print("\nNo records to remove.")
        return
    
    list_records(config)
    try:
        idx = int(input("\nEnter the number (#) of the record to remove: "))
        if 0 <= idx < len(records):
            removed = records.pop(idx)
            config["CLOUDFLARE_RECORDS"] = records
            save_config(config)
            print(f"Removed {removed['name']}.")
        else:
            print("Invalid index.")
    except ValueError:
        print("Please enter a valid number.")

def main():
    config = load_config()
    
    while True:
        print("\n=== Cloudflare Domain Manager ===")
        print("1. List subscribed domains")
        print("2. Add new domain/subdomain")
        print("3. Remove domain/subdomain")
        print("4. Exit")
        
        choice = input("\nSelect an option: ").strip()
        
        if choice == '1':
            list_records(config)
        elif choice == '2':
            add_record(config)
        elif choice == '3':
            remove_record(config)
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
