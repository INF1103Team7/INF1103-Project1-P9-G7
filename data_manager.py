import json

from pathlib import Path
from datetime import date, datetime, timedelta
import image_storage

#location of the JSON file used to store all lost and found reports
PROJECT_DIRECTORY = Path(__file__).resolve().parent

#set the location of the JSON file used to store reports
DATA_FILE = PROJECT_DIRECTORY / "reports_test.json"

#valid statues that a report can have
VALID_STATUSES = [
    "active",
    "claimed",
    "returned",
    "closed"
]

# loads all existing reports from reports.json
def load_reports():
    # if the reports file does not exist, returns an empty list
    if not DATA_FILE.is_file():
        return[]
    try:
        # open the JSON file for reading
        with DATA_FILE.open("r",encoding='utf-8') as file:
            # convert json data into python list
            reports = json.load(file)
        
        # ensures the JSON file contains a list of reports
        if not isinstance(reports,list):
            return []
        # returns all reports that were loaded
        return reports
    # prevents the program from crashing if the file is corrupt
    except (json.JSONDecodeError,OSError):
        return []

# saves the current lists of reports into to reports.json
def save_reports(reports):
    try:
        #opens reports.json in write mode
        with DATA_FILE.open("w", encoding="utf-8") as file:
            #save the report list as formatted JSON
            json.dump(reports, file, indent=4)
        # return true when the reports are saved successfully
        return True
    #return false if the file cannot be written
    except OSError:
        return False

# Add a new report and prevent duplicate case IDs
def add_report(report):

    reports = load_reports()
    stored_report = dict(report)

    # Generate a unique case ID if one does not exist
    case_id = stored_report.get("case_id")

    if not case_id:
        case_id = image_storage.create_case_id()
        stored_report["case_id"] = case_id

    # Prevent duplicate reports
    for existing_report in reports:
        if existing_report.get("case_id") == case_id:
            return False

    # New reports are active by default
    if "status" not in stored_report:
        stored_report["status"] = "active"

    reports.append(stored_report)

    return save_reports(reports)

# Find a specific report using its case ID
def get_report_by_id(case_id):
    reports = load_reports()

    for report in reports:
        if report.get("case_id") == case_id:
            return report

    return None

# Filter reports by lost or found type
def get_reports_by_type(report_type):
    reports = load_reports()

    matching_reports = []

    for report in reports:
        if report.get("report_type") == report_type:
            matching_reports.append(report)

    return matching_reports

# Return only reports that are currently active
def get_active_reports():
    reports = load_reports()

    active_reports = []

    for report in reports:
        if report.get("status") == "active":
            active_reports.append(report)

    return active_reports

# Update a report's status and record when it is closed
def update_report_status(case_id, new_status):

    if new_status not in VALID_STATUSES:
        return False

    reports = load_reports()
    for report in reports:
        if report.get("case_id") == case_id:
            report["status"] = new_status

            # Store the closure date for automatic deletion later
            if new_status == "closed":
                report["closed_date"] = date.today().isoformat()
            return save_reports(reports)
    return False

# Delete reports that have been closed longer than the retention period (30 days)
def delete_expired_reports(retention_days=30):
    reports = load_reports()
    remaining_reports = []
    deleted_count = 0
    
# Calculate the expiry date based on the retention period
    expiry_date = date.today() - timedelta(days=retention_days)

    for report in reports:
        if report.get("status") == "closed" and report.get("closed_date"):
            try:
                closed_date = datetime.strptime(
                    report["closed_date"],
                    "%Y-%m-%d"
                ).date()
                # Remove reports that have expired
                if closed_date <= expiry_date:
                    deleted_count += 1
                    continue

            except ValueError:
                pass

        remaining_reports.append(report)
    # Only update the file when a report has been deleted
    if deleted_count > 0:
        save_reports(remaining_reports)

    return deleted_count
    