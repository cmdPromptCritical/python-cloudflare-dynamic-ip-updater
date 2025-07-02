# Python script to manage dynamic IP addresses in Cloudflare DNS
(this fork runs in the background and pings for ip changes based on interval defined in config file)
Can be scheduled to run periodically using Cron jobs.

## Introduction

Use this script as a template for managing dynamic IP addresses in Cloudflare DNS using API v4.

Documentation about updating a DNS record through Cloudflare API v4 is available here: https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-update-dns-record.

## Installation

1. Generate a token for the Cloudflare API. For mor details, see https://developers.cloudflare.com/fundamentals/api/get-started/create-token/.

2. Verify the token:

```shell
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type:application/json"
```

2. Get your DNS zone's ID from your dashboard. For more details, see https://developers.cloudflare.com/fundamentals/setup/find-account-and-zone-ids/.

3. Get your DNS record's details using the API:

    - Only records of type `A` (IPv4) are supported by this script.

```shell
curl -X GET "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records" \
     -H "Authorization: Bearer {token}"
```

5. Copy the `config/config.sample.py` file to `config/config.py` and fill in the required information.

6. Install the required Python packages:

```shell
pip install -r requirements.txt
```

7. Test the script:

```shell
python cloudflare-dynamic-ip.py
```

It should generate a log file called `cloudflare-dynamic-ip.log` in the same directory.

## Usage

Run the script:

```shell
python cloudflare-dynamic-ip.py
```

## Cron

If you want to run the script programatically, you can use Cron jobs:

```shell
crontab -e
```

And add, for example:

```
@reboot /path/to/.venv/bin/python /path/to/cloudflare-dynamic-ip.py
0 0,12 * * * /path/to/.venv/bin/python /path/to/cloudflare-dynamic-ip.py
```

This Cron configuration will run the script at reboot and every day at 00:00 and 12:00.

## New Features

### IP Retrieval Functions

This repository now includes functions to retrieve the current IP address from Cloudflare DNS records:

- `get_ip_from_cloudflare_record()` - Get IP directly with zone ID, record name, and API token
- `get_ip_from_existing_record()` - Get IP using existing configuration format

For detailed documentation and examples, see [GET_IP_FUNCTIONS.md](docs/GET_IP_FUNCTIONS.md).

**Quick Example:**
```python
from cloudflare_dynamic_ip import get_ip_from_cloudflare_record

ip = get_ip_from_cloudflare_record("zone_id", "example.com", "api_token")
if ip:
    print(f"Current DNS record IP: {ip}")
```
