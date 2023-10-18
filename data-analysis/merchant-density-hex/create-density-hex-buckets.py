import requests
import json
import h3
import os

# Set the working directory to the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

# Step 1: Get Latest Merchants from btcmap.org/elements
url = "https://api.btcmap.org/elements"
response = requests.get(url)

# Check if the response status code indicates success
if response.status_code == 200:
    try:
        # Attempt to decode the JSON response
        data = response.json()

        # Create a dictionary to store the count of merchants in each hexagon
        hexagon_merchant_count = {}

        # Step 2: Extract Element ID and Position (Lon, Lat)
        for item in data:
            lon = item['osm_json'].get('lon', None)
            lat = item['osm_json'].get('lat', None)

            # Only process entries with valid location data
            if lon is not None and lat is not None:
                hex_id = h3.geo_to_h3(lat, lon, 8)  # Adjust the resolution as needed
                hexagon_merchant_count[hex_id] = hexagon_merchant_count.get(hex_id, 0) + 1

        # Create a list of dictionaries with hex center coordinates and merchant count
        hexagon_data = []
        for hex_id, merchant_count in hexagon_merchant_count.items():
            lat, lon = h3.h3_to_geo(hex_id)
            hexagon_data.append({
                "hex_id": hex_id,
                "latitude": lat,
                "longitude": lon,
                "merchant_count": merchant_count,
            })

        # Save the hexagon merchant count data as a JSON file
        with open("hex_merchant_data.json", "w") as json_file:
            json.dump(hexagon_data, json_file)

        print("Hexagon merchant count data exported as 'hexagon_merchant_count.json'.")
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
