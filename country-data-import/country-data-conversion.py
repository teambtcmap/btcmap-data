#This script takes GeoJSON country definitions sourced from https://github.com/AshKyd/geojson-regions and converts them to the BTC Map format.
#The area of the GeoJSON is calculated in KM^2 at the same time.

import os
import json
from area import area
from geojson_rewind import rewind

# Set the working directory to the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

# Specify the input directory containing the GeoJSON files
input_directory_path = 'input/geojson-regions-50m'

# Specify the output directory where you want to save the JSON files
output_directory_path = 'output/btcmap-areas-50m'

# Function to extract elements from a GeoJSON feature
def extract_elements(feature) -> None:
    # Convert "id" to lowercase
    id_lower = feature["properties"].get("iso_a2", "").lower()

    # Calculate the area of the geometry
    area_m2 = area(feature["geometry"])
    area_km2 = round((area_m2 / 1_000_000),2)

    #Ensure imported GeoJSON follows the RHR
    geo_json = rewind(feature["geometry"])
    
    extracted_feature = {
        "id": id_lower,
        "tags": {
            "type": "country",
            "iso_a2": feature["properties"].get("iso_a2", ""),
            "iso_a3": feature["properties"].get("iso_a3", ""),
            "wikidataid": feature["properties"].get("wikidataid", ""),
            "name": feature["properties"].get("admin", ""),
            "country_type": feature["properties"].get("type", ""),
            "sovereignt": feature["properties"].get("sovereignt", ""),
            "continent": feature["properties"].get("continent", ""),
            "region_un": feature["properties"].get("region_un", ""),
            "subregion": feature["properties"].get("subregion", ""),
            "region_wb": feature["properties"].get("region_wb", ""),
            "region_un": feature["properties"].get("region_un", ""),
            "lat": feature["properties"].get("label_y", ""),
            "lon": feature["properties"].get("label_x", ""),
            "area_km2": area_km2,
            "population": feature["properties"].get("pop_est", ""),
            "population:rank": feature["properties"].get("pop_rank", ""),
            "population:year": feature["properties"].get("pop_year", ""),
            "gdp_md": feature["properties"].get("gdp_md", ""),
            "gdp_year": feature["properties"].get("gdp_year", ""),
            "economy": feature["properties"].get("economy", ""),
            "income_grp": feature["properties"].get("income_grp", ""),
            "geo_json": geo_json
        }
    }
    
    return extracted_feature

# Iterate through files in the directory
for filename in os.listdir(input_directory_path):
    if filename.endswith(".geojson"):
        file_path = os.path.join(input_directory_path, filename)
        
        # Load the GeoJSON file
        with open(file_path, 'r') as file:
            geojson_data = json.load(file)
        
        # Check if "features" key exists in the GeoJSON data
        if "features" in geojson_data:
            # Process each feature in the GeoJSON data
            for feature in geojson_data['features']:
                extracted_feature = extract_elements(feature)
                id_lower = extracted_feature["id"]
                
                # Create an output filename in the format id.json
                output_filename = f"{id_lower}.json"
                
                # Write the extracted feature to a separate JSON file
                output_file_path = os.path.join(output_directory_path, output_filename)
                with open(output_file_path, 'w') as output_file:
                    json.dump(extracted_feature, output_file, indent=2)
        else:
            # If there is no "features" key, assume the entire file is a single feature
            extracted_feature = extract_elements(geojson_data)
            id_lower = extracted_feature["id"]
            
            # Create an output filename in the format id.json
            output_filename = f"{id_lower}.json"
            
            # Write the extracted feature to a separate JSON file in the output directory
            output_file_path = os.path.join(output_directory_path, output_filename)
            with open(output_file_path, 'w') as output_file:
                json.dump(extracted_feature, output_file, indent=2)

print("Separate JSON files created in the specified output directory.")