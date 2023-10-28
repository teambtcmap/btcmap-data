import requests
import csv
import os
import sys
from datetime import datetime
import json

class Area:
    def __init__(self, id, tags):
        self.id = id
        self.tags = tags
        self.reports = []
        self.population = tags.get('population')
        self.area_km2 = tags.get('area_km2')
        self.merchants_per_population = None
        self.merchants_per_km2 = None
        self.average_verification_age = None
        self.total_merchants = None

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
        self.average_verification_date = self.parse_date(report_data['tags'].get('avg_verification_date'))
        self.grade = report_data['tags'].get('grade')
        self.legacy_elements = report_data['tags'].get('legacy_elements')
        self.outdated_elements = report_data['tags'].get('outdated_elements')
        self.total_elements = report_data['tags'].get('total_elements')
        self.total_elements_lightning = report_data['tags'].get('total_elements_lightning')
        self.total_elements_lightning_contactless = report_data['tags'].get('total_elements_lightning_contactless')
        self.total_elements_onchain = report_data['tags'].get('total_elements_onchain')
        self.total_elements_atms = report_data['tags'].get('total_atms')
        self.up_to_date_elements = report_data['tags'].get('up_to_date_elements')
        self.up_to_date_percent = report_data['tags'].get('up_to_date_percent')

    def parse_date(self, date_string):
        if date_string:

            #Terrible hack because strptime is not handling 9 point decimal seconds well.
            date_only = date_string.split('T')[0]

            date_formats = ['%Y-%m-%d']

            for date_format in date_formats:
                try:
                    return datetime.strptime(date_only, date_format)
                except ValueError:
                    print(f"Failed to parse {date_only} with format {date_format}")
        return None


def get_areas():
    url = "https://api.btcmap.org/areas"
    headers = {
        'Content-Type': 'application.json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching areas: {response.text}")
        sys.exit(1)

    areas = response.json()
 
    global_area = []
    country_areas = []
    community_areas = []
    other_areas = []

    for id in areas:
        tags = id.get('tags', {})
        area_type = tags.get('type')

        if area_type == "country":
            id = id['id']
            area = Area(id, tags)
            country_areas.append(area)
        elif area_type == "community":
            id = id['id']
            area = Area(id, tags)
            community_areas.append(area)
        elif area_type == "" or area_type is None:
            id = id['id']
            area = Area(id, tags)
            other_areas.append(area)

    #Create a global area
    global_json = """
    {
        "name": "Global",
        "population:date": "2021-02-01",
        "url_alias": "global",
        "population": "6000000000",
        "area_km2": "149000000"
    }"""
    global_tags = json.loads(global_json)
    id = ""
    area = Area(id, global_tags)
    global_area.append(area)

    return global_area, country_areas, community_areas, other_areas


def get_reports(areas):
    
    updated_since_date = "2023-10-26"

    url = f"https://api.btcmap.org/reports/?updated_since={updated_since_date}"
    
    headers = {
        'Content-Type': 'application.json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching reports: {response.text}")
        sys.exit(1)

    report_data = response.json()
    for id in report_data:
        area_id = id['area_id']

        for area in areas:
            if area_id == area.id:
                area.add_report(Report(id))

def calculate_metrics(areas):
    for area in areas:
        latest_report = area.get_latest_report()
        if latest_report:

            #Calulate total *merchants*, excluding ATMs
            area.total_merchants = latest_report.total_elements - latest_report.total_elements_atms

            #Calulate average verification age
            if latest_report.average_verification_date:
                current_date = datetime.now()
                area.average_verification_age = (current_date - latest_report.average_verification_date).days
            else:
                area.average_verification_age = None

            # Calculate merchant denisty per capita
            if area.population and area.population != '0':
                area.merchants_per_population = latest_report.total_elements / float(area.population)
            else:
                area.merchants_per_population = None

            # Calculate merchant denisty per km2
            if area.area_km2 and area.area_km2 != '0':
                area.merchants_per_km2 = latest_report.total_elements / float(area.area_km2)
            else:
                area.merchants_per_km2 = None

def write_to_csv(areas, csv_file_path):
    with open(csv_file_path, mode="w", newline="") as csv_file:
        sample_row = areas[0] if areas else None
        fieldnames = [
            "id",
            "url_alias",
            "population",
            "area_km2",
            "id (Latest Report)",
            "date",
            "average_verification_date",
            "grade",
            "legacy_elements",
            "outdated_elements",
            "total_elements",
            "total_merchants",
            "total_elements_atms",
            "total_elements_lightning",
            "total_elements_lightning_contactless",
            "total_elements_onchain",
            "up_to_date_elements",
            "up_to_date_percent",
            "Average Verification Age (Days)",
            "Merchants per Population",
            "Merchants per km²"
        ]

        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        for area in areas:
            latest_report = area.get_latest_report()
            if latest_report:
                # Create a new dictionary containing the specified fields
                row = {
                    "id": area.id,
                    "url_alias": area.get_alias(),
                    "population": area.population,
                    "area_km2": area.area_km2,
                    "id (Latest Report)": latest_report.id,
                    "date": latest_report.date,
                    "average_verification_date": latest_report.average_verification_date,
                    "grade": latest_report.grade,
                    "legacy_elements": latest_report.legacy_elements,
                    "outdated_elements": latest_report.outdated_elements,
                    "total_elements": latest_report.total_elements,
                    "total_merchants": area.total_merchants,
                    "total_elements_atms": latest_report.total_elements_atms,
                    "total_elements_lightning": latest_report.total_elements_lightning,
                    "total_elements_lightning_contactless": latest_report.total_elements_lightning_contactless,
                    "total_elements_onchain": latest_report.total_elements_onchain,
                    "up_to_date_elements": latest_report.up_to_date_elements,
                    "up_to_date_percent": latest_report.up_to_date_percent,
                    "Average Verification Age (Days)": area.average_verification_age,
                    "Merchants per Population": area.merchants_per_population,
                    "Merchants per km²": area.merchants_per_km2
                }

                csv_writer.writerow(row)


def main():
    # Set the working directory to the script's directory
    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)

    global_area, country_areas, community_areas, other_areas = get_areas()

    get_reports(global_area + country_areas + community_areas + other_areas)

    calculate_metrics(global_area)
    calculate_metrics(country_areas)
    calculate_metrics(community_areas)
    calculate_metrics(other_areas)

    global_csv_file_path = f"{script_directory}/global_stats.csv"
    country_csv_file_path = f"{script_directory}/country_stats.csv"
    community_csv_file_path = f"{script_directory}/community_stats.csv"
    others_csv_file_path = f"{script_directory}/others_stats.csv"

    write_to_csv(global_area, global_csv_file_path)
    write_to_csv(country_areas, country_csv_file_path)
    write_to_csv(community_areas, community_csv_file_path)
    write_to_csv(other_areas, others_csv_file_path)

    print("Data saved.")

if __name__ == "__main__":
    main()
