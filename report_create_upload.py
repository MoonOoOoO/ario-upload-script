"""
This script creates and uploads reports to ARIO platform. The script first reads the report_list.csv file to get the list of reports to be created and uploaded. 
Then, iterate over the image folders for each report and creates a new report and uploads the images under the corresponding folder. 
"""
import os
import json
import requests
import pandas as pd
import threading
from datetime import datetime
from functools import partial
from concurrent.futures import ThreadPoolExecutor

threadLock = threading.Lock()
# generate all reports name from given CSV file
report_name = []
number_of_images = 0
df = pd.read_csv('report_list.csv')
# folder directory
FILE_DIR = "/home/images/"  # directory where images are stored
for d in df['folder_name']:
    name = d.split('_')
    report_name.append(name[2] + "_" + name[6])

print("Total of " + str(len(report_name)) + " to be created and uploaded")


# make post requests to create new reports (from the CSV file) under user ario, userid=1
headers = {'Content-Type': "application/json"}
report_api = "[ARIO_URL_HERE]/api/Report"


def upload_image(report_id, f, img):
    global number_of_images
    with threadLock:
        number_of_images += 1
        print("[" + str(number_of_images) + "] " + f + "/" + img)

    with open(FILE_DIR + f + "/" + img, "rb") as img:
        file_dict = {"file": img}
        r_image = requests.post(report_api + "/" + report_id + "/images", files=file_dict)


for rn, fn in zip(report_name, df['folder_name']):
    now = datetime.now().isoformat()
    params = {"name": rn,
              "date": now + "Z",
              "images": '[]',
              "shared": 'true',
              "reportDescription": {},
              "userId": '1'}
    r = requests.post(report_api, data=json.dumps(params), headers=headers)
    response = json.loads(r.text)
    r_id = str(response['id'])

    # list files under directory and make post requests to upload images to the current report
    files = os.listdir(FILE_DIR)

    for f in files:  # root directory contains sub-folders for each report
        if f == fn:  # match the current report folder name with the CSV file

            # list images under the current report folder
            images = os.listdir(FILE_DIR + f)

            # make post requests to upload images to the current report
            upload_func = partial(upload_image, r_id, f)
            with ThreadPoolExecutor(max_workers=2) as executor:
                results = [executor.submit(upload_func, img) for img in images]

    # after all images uploaded, compress current report into a zip file
    compress = requests.get(report_api + "/" + r_id + "/file")
    if compress.status_code == 200:
        print("[" + str(datetime.now().isoformat()) + "] Report " + rn + " has been created successfully")
    else:
        continue
