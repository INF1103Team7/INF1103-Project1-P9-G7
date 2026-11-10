# data_manager file to handle all data storage and retrieval operations for the lost and found reports.

# Imports
from pathlib import Path
from data_classes.data_manager_service import DataManagerService

# Constants
# location of the JSON file used to store all lost and found reports
PROJECT_DIRECTORY = Path(__file__).resolve().parent

# set the location of the JSON file used to store reports
DATA_FILE = PROJECT_DIRECTORY / "found_reports.json"

# set the location of the image storage directory
IMAGE_DIRECTORY = PROJECT_DIRECTORY / "images"

# set the location of the temporary storage directory for extraction
TEMP_DIRECTORY = PROJECT_DIRECTORY / "temp"

# valid image file extensions that can be stored
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

class DataManager:
    def __init__(self):
        # create a DataManagerService object
        self._manager = DataManagerService(DATA_FILE, IMAGE_DIRECTORY, TEMP_DIRECTORY, IMAGE_EXTENSIONS)
    
    # loads all existing reports from reports.json
    def load_reports(self):
        # load reports using the OOP method
        return self._manager.load_reports()

    # Save new reports to found_reports.json
    def save_new_reports(self, new_report):
        return self._manager.save_new_report(new_report)

    # saves the current lists of reports into to found_reports.json
    def save_report_list(self, reports):
        # Save the report list using the OOP method
        return self._manager.save_report_list(reports)

    # Filter reports by category
    def get_reports_by_category(self, report_category):
        # return active reports matching the selected category
        return self._manager.get_reports_by_category(report_category)

    # Return only reports that are currently active
    def get_active_reports(self):
        # retrieve only active reports
        return self._manager.get_active_reports()

    # Update a report's status and record when it is closed
    def update_report_status(self, case_id, new_status):
        # update the report status using the OOP method
        return self._manager.update_report_status(case_id, new_status)

    def delete_expired_reports(self, retention_days=30):
        # delete expired reports using the OOP method
        return self._manager.delete_expired_reports(retention_days)

    # Clear temporary directory
    def clear_temp_directory(self):
        # delete temporary files using the OOP method
        deleted_count = self._manager.clear_temp_directory(TEMP_DIRECTORY)

        # display the number of deleted files
        print(
            f"\n[+] Cleared {deleted_count} temporary file(s) "
            f"from {Path(TEMP_DIRECTORY).name}/"
        )

        return deleted_count

    def store_image(self, source_path, case_id):
        # store the image using the OOP method
        stored_filename = self._manager.store_image(source_path, case_id)
        return stored_filename
