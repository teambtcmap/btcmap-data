import requests
import json
import sys
import os

# Get the bearer token from the environment variable
btcmap_api_token = os.getenv("BTCMAP_API_TOKEN")

if not btcmap_api_token:
    print("Please set the BTCMAP_API_TOKEN environment variable.")
    sys.exit(1)

# Set the working directory to the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

data_directory = "upload"

# Loop through each file in the directory
for filename in os.listdir(data_directory):
    # Construct the full path to the file
    file_path = os.path.join(data_directory, filename)

    # Check if the item in the directory is a file (not a subdirectory)
    if os.path.isfile(file_path):
        # Read the content of the file
        with open(file_path, "r", encoding="iso-8859-1") as file:
            try:
                area_data = json.load(file)  # Load data from the file
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from file {filename}: {e}")
                continue  # Skip to the next file if JSON decoding fails

        # Define the API URL and headers
        url = "https://api.btcmap.org/areas"
        headers = {
            'Authorization': f'Bearer {btcmap_api_token}',
            'Content-Type': 'application/json'
        }

        # Convert the area_data to JSON payload
        json_payload = json.dumps(area_data)

        # Send the query to the BTC Map API to create the area
        response = requests.post(url, headers=headers, data=json_payload)

        # Check if the request was successful
        if response.status_code == 200:
            print(f"Created area from file: {filename}")
        else:
            print(f"Error creating area from file {filename}: {response.text}")
