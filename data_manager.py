# data_manager file to handle all data storage and retrieval operations for the lost and found reports..

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
    
    def load_reports(self) -> list[dict]:
        """_summary_
            Loads all existing reports from the JSON file.
        Returns:
            list[dict]: A list of dictionaries, each representing a report.
        """
        return self._manager.load_reports()

    def save_new_reports(self, new_report: dict) -> None:
        """_summary_
            Save new reports to found_reports.json
        Args:
            new_report (dict): A dictionary representing the new report to be saved.

        Returns:
            None
        """
        return self._manager.save_new_report(new_report)

    def save_report_list(self, reports: list[dict]) -> None:
        """_summary_
            Saves the current list of reports into found_reports.json
        Args:
            reports (list[dict]): A list of dictionaries, each representing a report.

        Returns:
            None
        """
        return self._manager.save_report_list(reports)

    def get_reports_by_category(self, report_category: str) -> list[dict]:
        """_summary_
            return active reports matching the selected category
        Args:
            report_category (str): The category of the report to filter by.

        Returns:
            list[dict]: A list of dictionaries, each representing a report that matches the specified category.
        """
        return self._manager.get_reports_by_category(report_category)

    def get_active_reports(self) -> list[dict]:
        """_summary_
            Retrieves all active reports from the database.
        Returns:
            list[dict]: A list of dictionaries, each representing an active report.
        """
        return self._manager.get_active_reports()

    def update_report_status(self, case_id: str, new_status: str) -> bool:
        """_summary_
            Updates the status of a report identified by its case ID.
        Args:
            case_id (str): The unique identifier of the report to update.
            new_status (str): The new status to set for the report.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        return self._manager.update_report_status(case_id, new_status)

    def delete_expired_reports(self, retention_days=30) -> int:
        """_summary_
            Deletes expired reports from the database.
        Args:
            retention_days (int): The number of days to retain reports before deleting them.

        Returns:
            int: The number of expired reports that were deleted.
        """
        return self._manager.delete_expired_reports(retention_days)

    def clear_temp_directory(self) -> int:
        """_summary_
            Clears the temporary directory used for storing extracted files.
        Returns:
            int: The number of files that were deleted.
        """
        deleted_count = self._manager.clear_temp_directory(TEMP_DIRECTORY)

        # display the number of deleted files
        print(
            f"\n[+] Cleared {deleted_count} temporary file(s) "
            f"from {Path(TEMP_DIRECTORY).name}/"
        )

        return deleted_count

    def store_image(self, source_path: str, case_id: str) -> str:
        """_summary_
            Stores an image file in the designated image directory.
        Args:
            source_path (str): The path to the image file to be stored.
            case_id (str): The unique identifier of the case to which the image belongs.

        Returns:
            str: The name of the stored image file.
        """
        # store the image using the OOP method
        stored_filename = self._manager.store_image(source_path, case_id)
        return stored_filename
