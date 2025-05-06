import requests
import json
import geopandas as gpd
from shapely.geometry import Point, Polygon, mapping
import h3
import os

# Set the working directory to the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

# Step 1: Get Latest Merchants from your URL
url = "https://api.btcmap.org/elements"
response = requests.get(url)

# Check if the response status code indicates success
if response.status_code == 200:
    try:
        # Attempt to decode the JSON response
        data = response.json()

        # Define the H3 resolution
        resolution = 2

        # Create a list to store features with hex center and hex polygon
        hexagon_features = {}

        # Step 2: Extract Element ID and Position (Lon, Lat)
        for item in data:
            lon = item['osm_json'].get('lon', None)
            lat = item['osm_json'].get('lat', None)

            # Only process entries with valid location data
            if lon is not None and lat is not None:
                hex_id = h3.geo_to_h3(lat, lon, resolution)

                # Create a Point geometry for the hexagon center
                center = Point(lon, lat)

                # Create a Polygon geometry for the hexagon
                polygon = Polygon(h3.h3_to_geo_boundary(
                    hex_id))  # Get the hexagon boundary

                # If the hex_id doesn't exist in hexagon_features, create an
                # entry
                if hex_id not in hexagon_features:
                    hexagon_features[hex_id] = {
                        "type": "Feature",
                        "properties": {
                            "hex_id": hex_id,
                            "merchant_count": 0,  # Initialize the count to zero
                        },
                        "geometry": {
                            "type": "GeometryCollection",
                            "geometries": [
                                mapping(center),
                                # Convert center to GeoJSON format
                            ],
                        },
                    }

                # Increment the merchant count for this hexagon
                hexagon_features[hex_id]["properties"]["merchant_count"] += 1

        # Convert the dictionary values to a list to form a FeatureCollection
        hexagon_feature_collection = list(hexagon_features.values())

        # Create a FeatureCollection
        feature_collection = {
            "type": "FeatureCollection",
            "features": hexagon_feature_collection,
        }

        # Specify the output file path with the script directory
        output_file_path = os.path.join(
            script_directory, "hexagon_merchant_data.geojson")

        # Save the GeoJSON data with both hex center and hex polygon
        with open(output_file_path, "w") as json_file:
            json.dump(feature_collection, json_file)

        print("Hexagon merchant data with center and polygon exported as 'hexagon_merchant_data.geojson'.")
        print(f"Number of hexagons: {len(hexagon_feature_collection)}")

    except json.JSONDecodeError:
        print("Error decoding JSON response.")

else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
