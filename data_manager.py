import json
import os

from pathlib import Path
from datetime import date, datetime, timedelta
import image_storage

PROJECT_DIRECTORY = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIRECTORY / "reports.json"

VALID_STATUSES = [
    "active",
    "claimed",
    "returned",
    "closed"
]

def load_reports():
    if not DATA_FILE.is_file():
        return[]
    try:
        with DATA_FILE.open("r",encoding='utf-8') as file:
            reports= json.load(file)
        
        if not isinstance(reports,list):
            return []
        
        return reports
    except (json.JSONDecodeError,OSError):
        return []
    
def save_reports(reports):
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(reports, file, indent=4)

        return True

    except OSError:
        return False

def add_report(report):
    reports = load_reports()

    stored_report=dict(report)
    
    case_id= stored_report.get("case_id")
    stored_report["case_id"]= case_id
    
    for existing_report in reports:
        if existing_report.get("case_id") == case_id:
            return False
    
    if "status" not in stored_report:
        stored_report["status"]="active"
    reports.append(report)

    return save_reports(reports)

def get_report_by_id(case_id):
    reports = load_reports()

    for report in reports:
        if report.get("case_id") == case_id:
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

def update_report_status(report_id, new_status):
    if new_status not in VALID_STATUSES:
        return False

    reports = load_reports()

    for report in reports:
        if report.get("report_id") == report_id:
            report["status"] = new_status
            return save_reports(reports)

    return False

def update_report_status(case_id,new_status):
    if new_status not in VALID_STATUSES:
        return False
    
    reports= load_reports
    
    for report in reports: 
        if report.get("case_id") == case_id:
            report["status"]= new_status
            
            if new_status == "closed":
                report["closed_date"]=date.today().isoformat()
            return save_reports(reports)
    return False

def delete_expired_reports(retention_days=30):
    reports = load_reports()
    remaining_reports = []
    deleted_count = 0

    expiry_date = date.today() - timedelta(days=retention_days)

    for report in reports:
        if report.get("status") == "closed" and report.get("closed_date"):
            try:
                closed_date = datetime.strptime(
                    report["closed_date"],
                    "%Y-%m-%d"
                ).date()

                if closed_date <= expiry_date:
                    deleted_count += 1
                    continue

            except ValueError:
                pass

        remaining_reports.append(report)

    if deleted_count > 0:
        save_reports(remaining_reports)

    return deleted_count
    