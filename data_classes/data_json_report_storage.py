# Data json report class

# Imports
import json
from pathlib import Path
from data_classes.data_report_storage import ReportStorage

class JsonReportStorage(ReportStorage):
    def __init__(self, file_path):
        super().__init__(file_path)
        
        # convert the file path into a Path object
        self._file_path = Path(file_path)
        
    def load_reports(self) -> list[dict]:
        """_summary_
            Loads all existing reports from the JSON file.
        
        Returns:
            list[dict]: A list of dictionaries, each representing a report.
        """
        # return an empty list if the file does not exist
        if not self._file_path.is_file():
            return []
        try:
        # open and read the JSON file
            with self._file_path.open("r", encoding="utf-8") as file:
                reports = json.load(file)
                    # Ensure the JSON data contains a list
            if not isinstance(reports, list):
             raise ValueError("Reports must be stored as a list")

            # ensure every report is a dictionary
            for report in reports:
                if not isinstance(report, dict):
                    raise ValueError("Each report must be a dictionary")

            return reports
        except (json.JSONDecodeError, ValueError, OSError) as error:
            print("Error loading reports:", error)
            raise
        
    def save_reports(self, reports: list[dict]) -> bool:
        """_summary_
            Saves the current list of reports into the JSON file.
        Args:
            reports (list[dict]): A list of dictionaries, each representing a report.

        Returns:
            bool: True if the reports were saved successfully, False otherwise.
        """
        try:
        # create the parent folder if it does not exist
            self._file_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )
        
        # save the report list into the JSON file
            with self._file_path.open("w", encoding="utf-8") as file:
                json.dump(reports, file, indent=2)

            return True
    
        except (OSError, TypeError, ValueError) as error:
            print("Error saving reports:", error)
            return False
