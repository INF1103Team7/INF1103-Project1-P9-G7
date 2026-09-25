import json
import os

DATA_FILE="data/reports.json"

def load_reports():
    if not os.path.exists(DATA_FILE):
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

def get_report_by_id(report_id):
    reports = load_reports()

    for report in reports:
        if report.get("report_id") == report_id:
            return report

    return None

def get_reports_by_type(report_type):
    reports = load_reports()

    matching_reports = []

    for report in reports:
        if report.get("report_type") == report_type:
            matching_reports.append(report)

    return matching_reports

def get_active_reports():
    reports = load_reports()

    active_reports = []

    for report in reports:
        if report.get("status") == "active":
            active_reports.append(report)

    return active_reports