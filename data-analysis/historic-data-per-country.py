### Writes a CSV containing a list of locations that currently accept BTC and the date we first saw them.

###TODO
### 1) The overpass query currently only selects nodes as the history API calls are element type specific and this code currenlty only returns history for nodes.
### 2) Add charting via matplotlib

import requests
import csv
import xml.etree.ElementTree as ET
from datetime import datetime

#Enter country *name* as defined https://wiki.openstreetmap.org/wiki/Nominatim/Country_Codes
country = "Italia"

# Build Overpass query to select nodes with your criteria
overpass_query = f"""
[out:json];
area["name"={country}]->.boundaryarea;
(
  n["currency:XBT"="yes"](area.boundaryarea);
);
out ids;
"""

# Send the query to the Overpass API to get a list of node IDs
response = requests.post("https://overpass-api.de/api/interpreter", data=overpass_query)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    
    # Extract the list of node IDs
    node_ids = [element["id"] for element in data["elements"]]
    
    # Initialize a list to store timestamps
    timestamps = []
    
    # Iterate through the list of node IDs
    for node_id in node_ids:
        # Define the URL for the OSM API's history endpoint for nodes
        history_url = f"https://www.openstreetmap.org/api/0.6/node/{node_id}/history"
        
        # Send a GET request to retrieve the changeset history
        history_response = requests.get(history_url)
        
        # Check if the history request was successful
        if history_response.status_code == 200:
            history_data = history_response.content.decode("utf-8")
            root = ET.fromstring(history_data)
            
            # Initialize a variable to store the earliest timestamp
            earliest_timestamp = None
            
            # Iterate through the changesets to find the earliest timestamp among the desired tags
            for element in root.iter("node"):
                for tag in element.findall("tag"):
                    if (
                        tag.get("k") in ["currency:bitcoin", "currency:XBT"]
                        and tag.get("v") == "yes"
                    ):
                        timestamp_str = element.get("timestamp")
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
                        if earliest_timestamp is None or timestamp < earliest_timestamp:
                            earliest_timestamp = timestamp
            
            # If we found a timestamp, append it to the list
            if earliest_timestamp is not None:
                timestamps.append((node_id, earliest_timestamp))
    
    # Sort timestamps by datetime
    timestamps.sort(key=lambda x: x[1])
    
    # Save the timestamps to a CSV file
    with open(country+".csv", "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Node ID", "Earliest Timestamp when tags were added"])
        for node_id, timestamp in timestamps:
            csv_writer.writerow([node_id, timestamp.strftime("%Y-%m-%d %H:%M:%S")])
    
    print(f"Data saved to {country}.csv")
else:
    print("Error: Unable to retrieve data from Overpass API")
