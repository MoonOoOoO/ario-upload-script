"""
delete all empty reports under giving user account
"""

import requests
import json

headers = {'Content-Type': "application/json"}
ARIO_URL = "[ARIO WEBSITE URL]"

ario_user_api = f"{ARIO_URL}/api/User/[USER ID]"  # specify USER ID here
ario_report_api = f"{ARIO_URL}/api/Report"

report_ids = []
r_user = requests.get(ario_user_api)
response = json.loads(r_user.text)
for r in response["reports"]:
    if len(r["images"]) == 0:
        report_ids.append(r["id"])

if len(report_ids) == 0:
    print("No empty report")
    exit(0)

for report_id in report_ids:
    r_del = requests.delete(ario_report_api + "/" + str(report_id))
    if r_del.status_code == 200:
        print("Report " + str(report_id) + " has been deleted.")
    else:
        continue
