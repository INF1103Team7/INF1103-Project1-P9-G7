import json
import os

DATA_FILE="data/reports.json"

def load_reports():
    if not os.paths.exists(DATA_FILE):
        return[]
    try:
        with open(DATA_FILE,"r") as file:
            reports= json.load(file)
        return reports
    except (json.JSONDecodeError,OSError):
        return []
    
def save_reports(reports):
    os.makedirs("data", exist_ok=True)

    try:
        with open(DATA_FILE, "w") as file:
            json.dump(reports, file, indent=4)

        return True

    except OSError:
        return False

def add_report(report):
    reports = load_reports()

    reports.append(report)

    return save_reports(reports)