import requests
import json
import sys
import os
from area import area
from geojson_rewind import rewind
#from python_rclone import Rclone

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

#Required variables
area_name = 'Area Name'
alias = 'area-name' #Usually in the format area-name.
area_type = 'community' #community or country
continent = 'europe' #Lowercase, hyphen-seperated. europe|north-america|south-america|asia|oceania
icon_type = 'jpeg'
population = 123456
population_date = "2024-01-01"

#Optional variables

organization = None
language = None

twitter_link = None
website_link = None
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
rss_link = None
phone_number = None
github_link = None
matrix_link = None

ln_address = None
tips_url = None

# Load in the GeoJSON
geo_json = """
{"type":"Polygon","coordinates":[[[6.317,52.305],[6.322,52.311],[6.34,52.32],[6.333,52.329],[6.331,52.336],[6.324,52.348],[6.324,52.354],[6.334,52.375],[6.352,52.386],[6.382,52.391],[6.392,52.409],[6.393,52.413],[6.386,52.418],[6.381,52.424],[6.38,52.43],[6.383,52.435],[6.391,52.439],[6.426,52.448],[6.432,52.456],[6.434,52.463],[6.437,52.465],[6.438,52.47],[6.447,52.48],[6.455,52.481],[6.462,52.485],[6.477,52.488],[6.486,52.487],[6.49,52.49],[6.495,52.491],[6.497,52.497],[6.5,52.5],[6.504,52.501],[6.555,52.498],[6.6,52.49],[6.609,52.486],[6.614,52.479],[6.616,52.479],[6.625,52.484],[6.637,52.482],[6.644,52.488],[6.644,52.492],[6.646,52.495],[6.661,52.503],[6.671,52.505],[6.695,52.496],[6.701,52.496],[6.719,52.489],[6.721,52.487],[6.726,52.487],[6.758,52.473],[6.772,52.47],[6.856,52.47],[6.862,52.466],[6.864,52.461],[6.894,52.456],[6.937,52.446],[6.944,52.446],[6.954,52.451],[6.96,52.457],[6.972,52.474],[6.983,52.479],[6.989,52.48],[7.001,52.473],[7.005,52.464],[7.007,52.463],[7.015,52.449],[7.019,52.436],[7.027,52.432],[7.031,52.428],[7.041,52.413],[7.046,52.411],[7.061,52.41],[7.067,52.405],[7.071,52.397],[7.073,52.396],[7.081,52.379],[7.083,52.368],[7.082,52.349],[7.08,52.345],[7.066,52.334],[7.064,52.327],[7.058,52.321],[7.056,52.31],[7.049,52.305],[7.048,52.302],[7.041,52.296],[7.037,52.289],[7.04,52.282],[7.039,52.278],[7.041,52.277],[7.05,52.263],[7.07,52.251],[7.074,52.247],[7.076,52.239],[7.07,52.229],[7.059,52.223],[7.039,52.217],[7.021,52.215],[7.008,52.218],[6.993,52.217],[6.99,52.215],[6.988,52.208],[6.984,52.204],[6.982,52.199],[6.958,52.173],[6.935,52.168],[6.916,52.168],[6.912,52.162],[6.89,52.15],[6.881,52.123],[6.871,52.119],[6.865,52.114],[6.856,52.11],[6.846,52.109],[6.714,52.108],[6.696,52.114],[6.675,52.116],[6.656,52.122],[6.652,52.131],[6.654,52.136],[6.663,52.145],[6.66,52.156],[6.661,52.158],[6.652,52.162],[6.649,52.162],[6.641,52.157],[6.632,52.161],[6.617,52.154],[6.611,52.153],[6.6,52.157],[6.595,52.162],[6.593,52.17],[6.588,52.172],[6.558,52.167],[6.521,52.171],[6.511,52.171],[6.499,52.167],[6.491,52.167],[6.485,52.171],[6.477,52.172],[6.473,52.174],[6.47,52.179],[6.467,52.18],[6.459,52.191],[6.451,52.193],[6.439,52.206],[6.425,52.213],[6.419,52.219],[6.417,52.224],[6.41,52.229],[6.408,52.233],[6.38,52.234],[6.368,52.245],[6.365,52.252],[6.356,52.257],[6.346,52.26],[6.342,52.262],[6.339,52.266],[6.323,52.273],[6.319,52.279],[6.317,52.301],[6.317,52.305]]]}
"""
geo_json = json.loads(geo_json)

#Ensure imported GeoJSON follows the RHR
geo_json = rewind(geo_json)

# Calculate the area of the geojson
area_m2 = area(geo_json)
area_km2 = round(area_m2 / 1_000_000)

# Create the area_data dictionary
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

# Remove elements with values set to None from the area_data dictionary
for key, value in list(area_data['tags'].items()):
    if value is None:
        del area_data['tags'][key]


# Convert the area_data to JSON payload
json_payload = json.dumps(area_data)

#Send the query to the BTC Map API to create the area
url = "https://api.btcmap.org/v3/areas"
headers = {
    'Authorization': f'Bearer {btcmap_api_token}',
    'Content-Type': 'application/json'
}
response = requests.post(url, headers=headers, data=json_payload)

# Check if the request was successful
if response.status_code == 200:
    print(f"Created {area_name}.")

    # Now upload area icon

    # Initialize Rclone with the remote configuration name
    # rclone = Rclone()

    # Define the source (local) and destination (remote)
    #source = script_directory+alias+"."+icon_type
    #destination = "btcmap-api:/srv/http/static.btcmap.org/images"

    # Use the sync method to transfer files
    #rclone.sync(source, destination)

    # Check the result
    #if rclone.check():
    #    print("File transferred successfully.")
    #else:
    #    print("Error transferring file.")
else:
    print(f"Error creating area: {response.text}")