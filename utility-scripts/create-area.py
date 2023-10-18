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
# Empty variables will be ignored and will not create empty elements in the JSON

#Required
area_name = "Portland Bitcoin Group"
alias = "portland_bitcoin_group" #Usually in the format area-name.
area_type = "community" #community or country
continent = "north-america" #Lowercase, hyphen-seperated. europe|north-america|south-america|asia|oceania
icon_type = "webp"
population = None
population_date = None

organization = None
language = None

twitter_link = None
website_link = None
email = None
telegram_link = None
signal_link = None
nostr_link = None
meetup_link = "https://www.meetup.com/Portland-Bitcoin-Group/"
discord_link = None
instagram_link = None
youtube_link = None
facebook_link = None
rss_link = None
phone_number = None
github_link = None
matrix_link = None

ln_address = None
tips_url = None

# Load in the GeoJSON from a file named alias.geojson in the script directory
geo_json_file = f"{alias}.geojson"
geo_json = None

try:
    with open(geo_json_file, "r") as file:
        geo_json = json.load(file)
except FileNotFoundError:
    print(f"GeoJSON file '{geo_json_file}' not found. Please make sure the file exists.")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Error loading GeoJSON from file: {e}")
    sys.exit(1)

#Ensure imported GeoJSON follows the RHR
geo_json = rewind(geo_json)

# Calculate the area of the geojson
area_m2 = area(geo_json)
area_km2 = round(area_m2 / 1_000_000)

# Create the area_data dictionary with conditional elements
area_data = {
    "tags": {
        "type": area_type,
        "name": area_name,
        "url_alias": alias,
        "continent": continent,
        "icon:square": f"https://static.btcmap.org/images/communities/{alias}.{icon_type}",
        "organization": organization,
        "language": language,
        "geo_json": geo_json,
        "area_km2": area_km2,
        "population": population,
        "population:date": population_date,
        "contact:twitter": twitter_link,
        "contact:website": website_link,
        "contact:email": email,
        "contact:telegram": telegram_link,
        "contact:signal": signal_link,
        "contact:nostr": nostr_link,
        "contact:meetup": meetup_link,
        "contact:discord": discord_link,
        "contact:instagram": instagram_link,
        "contact:youtube": youtube_link,
        "contact:facebook": facebook_link,
        "contact:rss": rss_link,
        "contact:phone": phone_number,
        "contact:github": github_link,
        "contact:matrix": matrix_link,
        "tips:lightning_address": ln_address,
        "tips:url": tips_url
    }
}

#TODO This is not working for some reason and so we are seeing null values in the JSON output
# Remove elements with values set to None from the area_data dictionary
for key, value in list(area_data.items()):
    if value is None:
        del area_data[key]


# Convert the area_data to JSON payload
json_payload = json.dumps(area_data)

print(json_payload)


#Send the query to the BTC Map API to create the area
url = "https://api.btcmap.org/areas"
headers = {
    'Authorization': f'Bearer {btcmap_api_token}',
    'Content-Type': 'application/json'
}
response = requests.post(url, headers=headers, data=json_payload)

# Check if the request was successful
if response.status_code == 200:
    print(f"Created area.")
else:
    print(f"Error creating area: {response.text}")