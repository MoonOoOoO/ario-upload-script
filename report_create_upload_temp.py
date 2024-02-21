"""
This temp script is reorgnized and modified from the original script to fit the needs of the project. 
It's not validated and may not work as expected.
"""
import os
import json
import requests
import threading
import pandas as pd

from functools import partial
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Lock for thread-safe printing
threadLock = threading.Lock()


def generate_report_names():
    # Function to generate report names from CSV file
    df = pd.read_csv('report_list.csv')
    report_names = []
    for folder_name in df['folder_name']:
        name_parts = folder_name.split('_')
        report_names.append(name_parts[2] + "_" + name_parts[6])
    print("Total of", len(report_names), "reports to be created and uploaded")
    return report_names


def upload_image(report_id, folder_name, img):
    # Function to upload an image to a report
    with threadLock:
        print("[" + str(upload_image.counter) + "] " + folder_name + "/" + img)
        upload_image.counter += 1

    with open(FILE_DIR + folder_name + "/" + img, "rb") as img_file:
        file_dict = {"file": img_file}
        r_image = requests.post(report_api + "/" + report_id + "/images", files=file_dict)


# Counter for uploaded images
upload_image.counter = 1


def create_report(report_name):
    # Function to create a report
    now = datetime.now().isoformat()
    params = {
        "name": report_name,
        "date": now + "Z",
        "images": '[]',
        "shared": 'true',
        "reportDescription": {},
        "userId": '1'
    }
    r = requests.post(report_api, data=json.dumps(params), headers=headers)
    response = json.loads(r.text)
    return response['id']


if __name__ == "__main__":
    # Folder directory where images are stored
    FILE_DIR = "/home/images/"
    # API endpoint for report creation
    report_api = "[ARIO_URL_HERE]/api/Report"
    # Headers for HTTP requests
    headers = {'Content-Type': "application/json"}

    # Generate report names from CSV
    report_names = generate_report_names()

    # Iterate over report names to create and upload reports
    for report_name in report_names:
        # Create report
        report_id = create_report(report_name)

        # List images under the current report folder
        report_folder = report_name.replace("_", "/")
        images = os.listdir(FILE_DIR + report_folder)

        # Upload images to the report
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(partial(upload_image, report_id, report_folder), images)

        # Compress the current report into a zip file
        compress = requests.get(report_api + "/" + report_id + "/file")
        if compress.status_code == 200:
            print("[" + str(datetime.now().isoformat()) + "] Report", report_name, "has been created successfully")
