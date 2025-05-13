import requests
import json
import sys
import os
from area import area
from geojson_rewind import rewind

# Set the working directory to the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

# Get the bearer token from the environment variable
btcmap_api_token = os.getenv("BTCMAP_API_TOKEN")

if not btcmap_api_token:
    print("Please set the BTCMAP_API_TOKEN environment variable.")
    sys.exit(1)

# Define your variables
area_name = 'BTC Isla'
alias = 'btc-isla'  # Usually in the format area-name.
area_type = 'community'  # community or country
continent = 'north-america'  # Lowercase, hyphen-separated.
icon_type = 'jpg'
population = 12642
population_date = '2010-01-01'

# Optional variables
organization = None
language = None
twitter_link = 'https://x.com/BTCisla'
website_link = 'https://geyser.fund/project/btcisla'
email = None
telegram_link = None
signal_link = None
whatsapp_link = None
nostr_link = None
meetup_link = None
discord_link = None
instagram_link = None
youtube_link = None
facebook_link = None
linkedin_link = None
rss_link = None
phone_number = None
github_link = None
matrix_link = None

ln_address = 'btcisla@geyser.fund'
tips_url = None

# Load in the GeoJSON
geo_json = """
{"type":"Polygon","coordinates":[[[-86.76,21.285],[-86.74,21.285],[-86.73,21.275],[-86.725,21.255],[-86.71,21.245],[-86.69,21.21],[-86.69,21.195],[-86.705,21.18],[-86.735,21.19],[-86.74,21.205],[-86.755,21.215],[-86.775,21.255],[-86.77,21.265],[-86.76,21.285]]]}
"""
geo_json = json.loads(geo_json)

# Ensure imported GeoJSON follows the RHR
geo_json = rewind(geo_json)

# Calculate the area of the geojson
area_m2 = area(geo_json)
area_km2 = round(area_m2 / 1_000_000)

# Create the params dictionary for the JSON-RPC request
params = {
    "token": btcmap_api_token,
    "tags": {
        "type": area_type,
        "name": area_name,
        "url_alias": alias,
        "continent": continent,
        "geo_json": geo_json,
        "area_km2": area_km2,
        "population": population,
        "population:date": population_date,
        "organization": organization,
        "language": language,
        "contact:twitter": twitter_link,
        "contact:website": website_link,
        "contact:email": email,
        "contact:telegram": telegram_link,
        "contact:signal": signal_link,
        "contact:whatsapp": whatsapp_link,
        "contact:nostr": nostr_link,
        "contact:meetup": meetup_link,
        "contact:discord": discord_link,
        "contact:instagram": instagram_link,
        "contact:youtube": youtube_link,
        "contact:facebook": facebook_link,
        "contact:linkedin": linkedin_link,
        "contact:rss": rss_link,
        "contact:phone": phone_number,
        "contact:github": github_link,
        "contact:matrix": matrix_link,
        "tips:lightning_address": ln_address,
        "tips:url": tips_url
    }
}

# Remove elements with values set to None from the params dictionary
params['tags'] = {k: v for k, v in params['tags'].items() if v is not None}

# Create the JSON-RPC payload
json_rpc_payload = {
    "jsonrpc": "2.0",
    "method": "addarea",
    "params": params,
    "id": 1
}

# Convert the payload to JSON
json_payload = json.dumps(json_rpc_payload)

print(json_rpc_payload)

# Send the query to the BTC Map API to create the area
url = "https://api.btcmap.org/rpc"
headers = {
    'Content-Type': 'application/json'
}
response = requests.post(url, headers=headers, data=json_payload)

# Check if the request was successful
if response.status_code == 200:
    response_data = response.json()
    if 'result' in response_data:
        print(f"Created {area_name}.")
    else:
        print(f"Error creating area: {response_data.get('error', 'Unknown error')}")
else:
    print(f"HTTP Error: {response.status_code} - {response.text}")
