import requests
import csv
import os
import sys

class Area:
    def __init__(self, id, tags):
        self.id = id
        self.tags = tags
        self.reports = []

    def get_alias(self):
        alias = self.tags.get('url_alias', {})
        return alias

    def add_report(self, report):
        self.reports.append(report)

    def get_latest_report(self):
        if self.reports:
            return max(self.reports, key=lambda report: report.date)

class Report:
    def __init__(self, report_data):
        self.id = report_data['id']
        self.date = report_data['date']
        self.avg_verification_date = report_data['tags'].get('avg_verification_date')
        self.grade = report_data['tags'].get('grade')
        self.legacy_elements = report_data['tags'].get('legacy_elements')
        self.outdated_elements = report_data['tags'].get('outdated_elements')
        self.total_elements = report_data['tags'].get('total_elements')
        self.total_elements_lightning = report_data['tags'].get('total_elements_lightning')
        self.total_elements_lightning_contactless = report_data['tags'].get('total_elements_lightning_contactless')
        self.total_elements_onchain = report_data['tags'].get('total_elements_onchain')
        self.up_to_date_elements = report_data['tags'].get('up_to_date_elements')
        self.up_to_date_percent = report_data['tags'].get('up_to_date_percent')

# Define the area objects list globally
area_objects = []

# Fetch area data and reports
def get_countries():
    url = "https://api.btcmap.org/areas"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching areas: {response.text}")
        sys.exit(1)

    areas = response.json()
    area_filter = "country"
    for data in areas:
        tags = data.get('tags', {})
        area_type = tags.get('type')

        if area_type == area_filter:
            id = data['id']
            area = Area(id, tags)
            area_objects.append(area)

    return area_objects

def get_reports():
    url = "https://api.btcmap.org/reports"
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching reports: {response.text}")
        sys.exit(1)

    report_data = response.json()
    for id in report_data:
        area_id = id['area_id']
        for area in area_objects:
            if area_id == area.id:
                area.add_report(Report(id))

# Set the working directory to the script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

# Define the CSV file path
csv_file_path = "county_stats.csv"

# Fetch area data first
area_objects = get_countries()

# Fetch reports after area data is fetched
get_reports()

# Create and open the CSV file for writing
with open(csv_file_path, mode="w", newline="") as csv_file:
    # Extract unique keys from Latest Report Tags for fieldnames
    unique_keys = set()
    for country in area_objects:
        latest_report = country.get_latest_report()
        if latest_report:
            unique_keys.update(vars(latest_report).keys())
    
    # Define the CSV fieldnames including unique keys
    fieldnames = ["Country ID", "Latest Report ID", "Latest Report Date"] + list(unique_keys)
    
    # Create a CSV writer
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    # Write the header row
    csv_writer.writeheader()
    
    # Iterate through the area objects and write the latest report to the CSV
    for country in area_objects:
        latest_report = country.get_latest_report()
        if latest_report:
            row = {
                "Country ID": country.id,
                "Latest Report ID": latest_report.id,
                "Latest Report Date": latest_report.date
            }
            row.update(vars(latest_report))
            csv_writer.writerow(row)

print(f"Data saved to {csv_file_path}")
