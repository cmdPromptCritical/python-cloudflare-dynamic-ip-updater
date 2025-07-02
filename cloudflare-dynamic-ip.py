import json
import logging
from logging.handlers import RotatingFileHandler
import time

import requests
import cloudflare

from config.config import CLOUDFLARE_ZONES, LOGGING_LEVEL, LAST_IP_FILE, CURRENT_IP_API, CLOUDFLARE_RECORDS, \
    LOG_FILE, PING_INTERVAL_MINUTES

logger = logging.getLogger(__name__)


def update_record(record: dict, current_ip: str) -> bool:
    zone = CLOUDFLARE_ZONES[record["zone_id"]]

    logger.info("Updating record: {} in zone: {}".format(record["name"], zone["name"]))

    data = {
        "type": "A",
        "name": record["name"],
        "content": current_ip,
        "ttl": 1,  # Automatic
        "proxied": record["proxied"]
    }

    headers = {
        "Authorization": "Bearer {}".format(zone["token"]),
        "Content-Type": "application/json"
    }

    # See:  https://api.cloudflare.com/#dns-records-for-a-zone-update-dns-record
    url = "https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}".format(zone["id"], record["id"])

    response = requests.put(url=url, data=json.dumps(data), headers=headers)

    if "success" in response.json() and response.json()["success"]:
        logger.info("Record updated successfully")

        return True

    logger.error("Failed to update record")

    return False


def get_last_ip() -> str|None:
    ip = None

    try:
        with open(LAST_IP_FILE, "r") as file:
            ip = file.readline()
    except:
        pass

    logger.info("Last IP: {}".format(ip))

    return ip


def update_last_ip(ip: str) -> None:
    logger.info("Saving current IP...")

    with open(LAST_IP_FILE, "w") as file:
        file.write(ip)
        file.close()

    logger.info("Current IP saved")


def get_current_ip() -> str:
    ip = requests.get(CURRENT_IP_API).text

    logger.info("Current IP: {}".format(ip))

    return ip


def get_ip_from_cloudflare_record(zone_id: str, record_name: str, api_token: str) -> str | None:
    """
    Get the current IP address from a Cloudflare DNS record.
    
    Args:
        zone_id (str): The Cloudflare zone ID
        record_name (str): The DNS record name (e.g., 'example.com' or 'subdomain.example.com')
        api_token (str): The Cloudflare API token with Zone:Read permissions
    
    Returns:
        str | None: The IP address from the DNS record, or None if not found or error occurred
    """
    try:
        # Initialize Cloudflare client
        cf = cloudflare.Cloudflare(api_token=api_token)
        
        # Get DNS records for the zone
        records = cf.dns.records.list(zone_id=zone_id, name=record_name, type="A")
        
        if not records.result:
            logger.warning(f"No A record found for {record_name} in zone {zone_id}")
            return None
        
        # Get the first A record (there should typically be only one)
        record = records.result[0]
        ip_address = record.content
        
        logger.info(f"Retrieved IP from Cloudflare DNS record {record_name}: {ip_address}")
        return ip_address
        
    except Exception as e:
        logger.error(f"Failed to get IP from Cloudflare DNS record {record_name}: {str(e)}")
        return None


def get_ip_from_existing_record(record_config: dict) -> str | None:
    """
    Get the current IP address from a Cloudflare DNS record using existing configuration.
    
    Args:
        record_config (dict): Record configuration from CLOUDFLARE_RECORDS with keys:
                             - id: record ID
                             - zone_id: zone ID
                             - name: record name
    
    Returns:
        str | None: The IP address from the DNS record, or None if not found or error occurred
    """
    try:
        zone_id = record_config["zone_id"]
        record_name = record_config["name"]
        
        # Get zone configuration
        if zone_id not in CLOUDFLARE_ZONES:
            logger.error(f"Zone {zone_id} not found in CLOUDFLARE_ZONES configuration")
            return None
        
        zone_config = CLOUDFLARE_ZONES[zone_id]
        api_token = zone_config["token"]
        
        return get_ip_from_cloudflare_record(zone_id, record_name, api_token)
        
    except KeyError as e:
        logger.error(f"Missing required key in record configuration: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Failed to get IP from existing record configuration: {str(e)}")
        return None


def run() -> None:
    logger.info("Running...")

    last_ip = get_last_ip()
    current_ip = get_current_ip()

    if current_ip == last_ip:
        logger.info("IP has not changed. Exiting...")

        return

    any_failures = False

    for record in CLOUDFLARE_RECORDS:
        result = update_record(record, current_ip)

        if not result:
            any_failures = True
            break

    if not any_failures:
        update_last_ip(current_ip)

        logger.info("All records updated successfully. Exiting...")
    else:
        logger.error("Failed to update some records. Exiting...")


def set_up_logging() -> None:
    global logger

    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    handler = RotatingFileHandler(filename=LOG_FILE, mode="a", maxBytes=209 * 90, backupCount=2)
    handler.setFormatter(formatter)
    logger.setLevel(LOGGING_LEVEL)
    logger.addHandler(handler)


if __name__ == "__main__":
    set_up_logging()

    if (PING_INTERVAL_MINUTES):
        while True:
            run()
            time.sleep(PING_INTERVAL_MINUTES*60)