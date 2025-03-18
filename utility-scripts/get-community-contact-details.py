# Gets email, twitter and nosrt contact details for communities.

import requests
import csv
import os
import sys

# Set the working directory to the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

# Define the API URL to fetch all areas
url = "https://api.btcmap.org/areas"
headers = {
    'Content-Type': 'application/json'
}

# Send a GET request to fetch all areas
response = requests.get(url)

if response.status_code != 200:
    print(f"Error fetching areas: {response.text}")
    sys.exit(1)

# Parse the response JSON
areas = response.json()

# Define the area type to filter (replace with your values)
area_type_filter = "community"

# Create a CSV file to write the data
with open('areas_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['Area Alias', 'Email', 'Twitter', 'Nostr']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    for area in areas:
        tags = area.get('tags', {})
        area_type = tags.get('type', '')

        if area_type == area_type_filter:
            area_alias = tags.get('url_alias', '')
            email = tags.get('contact:email', '')
            twitter_url = tags.get('contact:twitter', '')
            nostr = tags.get('contact:nostr', '')

            # Extract the Twitter username from the URL
            twitter_username = ''
            if twitter_url and '/' in twitter_url:
                twitter_username = twitter_url.split('/')[-1].strip('@')

            if twitter_username:
                twitter_username = f'@{twitter_username}'

            writer.writerow({'Area Alias': area_alias,
                             'Email': email,
                             'Twitter': twitter_username,
                             'Nostr': nostr})

print("CSV file 'community_contact_details.csv' has been created.")
