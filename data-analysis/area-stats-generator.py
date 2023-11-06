import requests
import csv
import os
import sys
from datetime import datetime
import json
import matplotlib.pyplot as plt
import math

class Area:
    def __init__(self, id, tags):
        self.id = id
        self.alias = tags.get('url_alias')
        self.name = tags.get('name')
        self.tags = tags
        self.reports = []
        self.population = tags.get('population')
        self.area_km2 = tags.get('area_km2')
        self.merchants_per_capita = None
        self.merchants_per_km2 = None
        self.average_verification_age = None
        self.weighted_average_verification_age = None
        self.total_merchants = None
        self.weighted_total_merchants = None
        self.score = None

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

# Function to check if a JSON file exists and load data from it
def load_json_from_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            data = json.load(file)
            return data
    else:
        return None

# Function to save JSON data to a file
def save_json_to_file(data, file_name):
    with open(file_name, 'w') as file:
        json.dump(data, file)

def get_areas():
    
    # Check if areas.json exists and load data
    areas = load_json_from_file('areas.json')

    if areas is None:
        # areas.json doesn't exist, make API call and save data to the file
        
        url = "https://api.btcmap.org/areas"
        headers = {
            'Content-Type': 'application.json'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error fetching areas: {response.text}")
            sys.exit(1)

        areas = response.json()

    # Save the data to areas.json
    save_json_to_file(areas, 'areas.json')
 
    global_area = []
    country_areas = []
    community_areas = []
    other_areas = []

    for id in areas:
        tags = id.get('tags', {})
        area_type = tags.get('type')
        #deleted = 'deleted_at' in id and id['deleted_at'] == ""

        #ToDo make this IF work
        #if not deleted: #Only process areas that have not been deleted
        if area_type == "country":  
            id = id['id']
            area = Area(id, tags)
            country_areas.append(area)
        elif area_type == "community":
            id = id['id']
            area = Area(id, tags)
            community_areas.append(area)
        else:
            id = id['id']
            area = Area(id, tags)
            other_areas.append(area)

    #Link this in with the global area Igor created
    # #Create a global area
    global_json = """
    {
        "name": "Global",
        "population:date": "2021-02-01",
        "url_alias": "global",
        "population": 8000000000,
        "area_km2": 148900000
    }"""
    global_tags = json.loads(global_json)
    id = ""
    area = Area(id, global_tags)
    global_area.append(area)

    return global_area, country_areas, community_areas, other_areas


def get_reports(areas):
    
    updated_since_date = "2023-11-01"

     # Check if areas.json exists and load data
    reports = load_json_from_file('reports.json')

    if reports is None:
        # reports.json doesn't exist, make API call and save data to the file
        
        url = f"https://api.btcmap.org/reports/?updated_since={updated_since_date}"
        headers = {
            'Content-Type': 'application.json'
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error fetching areas: {response.text}")
            sys.exit(1)

        reports = response.json()

    # Save the data to areas.json
    save_json_to_file(reports, 'reports.json')

    for id in reports:
        area_id = id['area_id']

        for area in areas:
            if area_id == area.id:
                area.add_report(Report(id))

def calculate_metrics(areas):
    for area in areas:
        latest_report = area.get_latest_report()
        if latest_report:
            # Calculate total *merchants*, excluding ATMs
            area.total_merchants = latest_report.total_elements - latest_report.total_elements_atms

            # Calculate weighted merchants
            area.weighted_total_merchants = area.total_merchants * (latest_report.up_to_date_percent / 100)

            # Calculate average verification age
            if latest_report.average_verification_date:
                current_date = datetime.now()
                area.average_verification_age = (current_date - latest_report.average_verification_date).days
            else:
                area.average_verification_age = None

            # Calculate a weighted average verification age assuming all outdated elements do not have an average verification date
            average_outdated_element_age = 1 * 365  # This should be modified in time to use the last date a bitcoin tag was added to an element should a verification date not be present. This will get more inaccurate over time from Nov 2023, which is 12-months after the verification tags started being added

            if (latest_report.up_to_date_elements is not None and area.average_verification_age is not None and latest_report.outdated_elements is not None):
                weighted_average_verification_age = ((latest_report.up_to_date_elements * area.average_verification_age) + (latest_report.outdated_elements * average_outdated_element_age)) / latest_report.total_elements if latest_report.total_elements > 0 else None
                area.weighted_average_verification_age = weighted_average_verification_age
            else:
                area.weighted_average_verification_age = None

            # Calculate merchant density per capita
            if area.population and area.population != '0':
                area.merchants_per_capita = area.total_merchants / float(area.population)
            else:
                area.merchants_per_capita = None

            # Calculate merchant density per km2
            if area.area_km2 and area.area_km2 != '0':
                area.merchants_per_km2 = area.total_merchants / area.area_km2
            else:
                area.merchants_per_km2 = None
        

            # Calculate area score based on the current set of areas

            # Filter out areas with None values for weighted_total_merchants
            valid_areas = [area for area in areas if area.weighted_total_merchants is not None]

            if valid_areas:
                max_weighted_total_merchants = max(area.weighted_total_merchants for area in valid_areas)

                if max_weighted_total_merchants == 0:
                    for area in areas:
                        area.score = 0
                else:
                    for area in areas:
                        if area.weighted_total_merchants is not None:
                            normalized_score = area.weighted_total_merchants / max_weighted_total_merchants
                            area.score = normalized_score
            else:
                # Handle the case where there are no valid areas with non-None values
                for area in areas:
            
                    area.score = 0



            
 
         
def plot_total_elements_over_time(areas):
    for area in areas:
        x = [report.date for report in area.reports]
        y = [report.total_elements for report in area.reports]
        plt.plot(x, y, label=area.id)

    plt.xlabel('Date')
    plt.ylabel('Total Elements')
    plt.title('Total Elements Over Time')
    plt.legend()

    # Adjust the following path and filename as needed
    filename = 'total_elements_chart.png'
    #plt.savefig(filename)

    #plt.show()  # Optionally display the chart on the screen


def write_to_csv(areas, csv_file_path):
    with open(csv_file_path, mode="w", newline="") as csv_file:
        sample_row = areas[0] if areas else None
        fieldnames = [
            "id",
            "name",
            "Weighted Average Verification Age (Days)",
            "Merchants per Capita",
            "Merchants per km²",
            "Score",
            "population",
            "area_km2",
            "total_merchants",
            "weighted_total_merchants",
            "up_to_date_elements",
            "up_to_date_percent",
            "Average Verification Age (Days)",
            "id (Latest Report)",
            "date",
            "average_verification_date",
            "grade",
            "legacy_elements",
            "outdated_elements",
            "total_elements",
            "total_elements_atms",
            "total_elements_lightning",
            "total_elements_lightning_contactless",
            "total_elements_onchain"
        ]

        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()

        for area in areas:
            latest_report = area.get_latest_report()
            if latest_report:
                # Create a new dictionary containing the specified fields
                row = {
                    "id": area.id,
                    "name": area.name,
                    "population": area.population,
                    "Weighted Average Verification Age (Days)": round(area.weighted_average_verification_age, 2) if area.weighted_average_verification_age is not None else 0,
                    "Merchants per Capita": "{:.10f}".format(area.merchants_per_capita) if area.merchants_per_capita is not None else 0,
                    "Merchants per km²": "{:.10f}".format(area.merchants_per_km2) if area.merchants_per_km2 is not None else 0,
                    "Score": area.score,
                    "area_km2": area.area_km2,
                    "total_merchants": area.total_merchants,
                    "weighted_total_merchants": area.weighted_total_merchants,
                    "up_to_date_elements": latest_report.up_to_date_elements,
                    "up_to_date_percent": latest_report.up_to_date_percent,
                    "Average Verification Age (Days)": str(area.average_verification_age),
                    "id (Latest Report)": latest_report.id,
                    "date": latest_report.date,
                    "average_verification_date": latest_report.average_verification_date,
                    "grade": latest_report.grade,
                    "legacy_elements": latest_report.legacy_elements,
                    "outdated_elements": latest_report.outdated_elements,
                    "total_elements": latest_report.total_elements,
                    "total_elements_atms": latest_report.total_elements_atms,
                    "total_elements_lightning": latest_report.total_elements_lightning,
                    "total_elements_lightning_contactless": latest_report.total_elements_lightning_contactless,
                    "total_elements_onchain": latest_report.total_elements_onchain
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

    plot_total_elements_over_time(community_areas)

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
