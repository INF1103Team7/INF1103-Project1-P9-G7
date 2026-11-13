import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

from data_classes.data_json_report_storage import JsonReportStorage
from data_classes.data_report import Report
from data_classes.data_report_storage import ReportStorage


class DataManagerService:
    def __init__(
        self,
        reports_file: str,
        image_directory: Path,
        temp_directory: Path,
        image_extensions: list[str],
        storage: ReportStorage | None = None
    ):
        # Use the provided storage or default to JSON storage
        self._storage = storage if storage is not None else JsonReportStorage(reports_file)

        self._image_directory = Path(image_directory)
        self._image_extensions = image_extensions
        self._temp_directory = Path(temp_directory)
    
    def load_reports(self) -> list[dict]:
        """_summary_
            Loads all existing reports from the JSON file.
        
        Returns:
            list[dict]: A list of dictionaries, each representing a report.
        """
        return self._storage.load_reports()
    
    def save_report_list(self, reports: list[dict]) -> bool:
        """_summary_
            Saves the current list of reports into the JSON file.
        Args:
            reports (list[dict]): A list of dictionaries, each representing a report.

        Returns:
            bool: True if the reports were saved successfully, False otherwise.
        """
        return self._storage.save_reports(reports)
    
    def save_new_report(self, report_data: dict) -> dict | None:
        """_summary_
            Save new reports to found_reports.json
        Args:
            new_report (dict): A dictionary representing the new report to be saved.

        Returns:
            None
        """
        # create a Report object
        report = Report(report_data)
        # convert the report into a dictionary
        stored_report = report.to_dict()

        # check whether an image was provided
        source_path = stored_report.get("image_path")
        if source_path is not None:
            if not isinstance(source_path, str):
                raise ValueError("Image path must be a string")

            image_filename = self.store_image(source_path, report.get_case_id())

            if image_filename is None:
                print("[!] Report not saved because the image could not be stored.")
                return None

            stored_report["image_filename"] = image_filename

        # remove the original image path
        stored_report.pop("image_path", None)

        # load existing reports
        reports = self.load_reports()

        # add the new report
        reports.append(stored_report)

        # save the updated report list
        if self.save_report_list(reports):
            return stored_report

        return None
    
    def store_image(self, source_path: str | Path, case_id: str | None) -> str | None:
        """Store an image in the images or temporary directory."""

        source = Path(source_path)

        if source.suffix.lower() not in self._image_extensions:
            print("[!] Only JPG, JPEG, and PNG images can be stored.")
            return None

        if not source.is_file():
            print(f"[!] Image not found: {source}")
            return None

        if case_id:
            destination_directory = Path(self._image_directory)
            stored_filename = f"{case_id}{source.suffix.lower()}"
        else:
            destination_directory = Path(self._temp_directory)
            stored_filename = source.name

        destination = destination_directory / stored_filename

        try:
            destination_directory.mkdir(parents=True, exist_ok=True)

            if source.resolve() != destination.resolve():
                shutil.copy2(source, destination)

            return stored_filename

        except OSError as error:
            print(f"[!] Error storing image: {error}")
            return None
        
    def get_active_reports(self) -> list[dict]:
        """_summary_
            return active reports from the database
        Returns:
            dict: list[dict]: A list of dictionaries, each representing an active report.
        """
        active_reports = []

        for report in self.load_reports():
            if report.get("status") == "active":
                active_reports.append(report)

        return active_reports

    def get_reports_by_category(self, category: str) -> list[dict]:
        """_summary_
            return active reports matching the selected category
        Args:
            report_category (str): The category of the report to filter by.

        Returns:
            list[dict]: A list of dictionaries, each representing a report that matches the specified category.
        """
        matching_reports = []

        for report in self.get_active_reports():
            if report.get("category") == category:
                matching_reports.append(report)

        return matching_reports
    
    def get_report_by_id(self, case_id: str) -> dict | None:
        """_summary_
            Function to retrieve a report by its case ID from the database.
        Args:
            case_id (str): The unique identifier of the report to retrieve.

        Returns:
            dict | None: The report if found, otherwise None.
        """
        for report in self.load_reports():
            if report.get("case_id") == case_id:
                return report
        return None

    def update_report_status(self, case_id: str, new_status: str) -> bool:
        """_summary_
            Updates the status of a report identified by its case ID.
        Args:
            case_id (str): The unique identifier of the report to update.
            new_status (str): The new status to set for the report.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        reports = self.load_reports()

        for index in range(len(reports)):
            if reports[index].get("case_id") == case_id:
                # create a Report object to update its status
                report = Report(reports[index])

                if not report.update_status(new_status):
                    return False

                reports[index] = report.to_dict()

                return self.save_report_list(reports)

        return False
    
    def delete_expired_reports(self, retention_days=30) -> int:
        """_summary_
            Function to delete expired reports from the database based on a specified retention period. It also deletes associated image files if they exist.
        Args:
            retention_days (int, optional): The number of days to retain reports before deleting them. Defaults to 30.

        Returns:
            int: The number of reports deleted. Returns 0 if no reports were deleted or if an error occurred.
        """
        if type(retention_days) is not int or retention_days < 0:
            print("[!] Error: Retention days must be a non-negative integer, using default 30 days")
            retention_days = 30

        reports = self.load_reports()
        remaining_reports = []
        expired_reports = []

        expiry_date = date.today() - timedelta(days=retention_days)

        for report in reports:
            expired = False

            if report.get("status") == "closed":
                closed_date = report.get("closed_date")

                if closed_date:
                    try:
                        closed_date = datetime.strptime(
                            closed_date, "%Y-%m-%d"
                        ).date()

                        if closed_date <= expiry_date:
                            expired = True

                    except (ValueError, TypeError):
                        print("Invalid closed date in report")

            if expired:
                expired_reports.append(report)
            else:
                remaining_reports.append(report)

        if len(expired_reports) == 0:
            return 0

        if not self.save_report_list(remaining_reports):
            return 0

        for report in expired_reports:
            image_filename = report.get("image_filename")

            if image_filename and isinstance(image_filename, str):
                image_path = self._image_directory / image_filename

                try:
                    if image_path.parent.resolve() != self._image_directory.resolve():
                        print("Invalid image filename:", image_filename)
                        continue

                    if image_path.is_file():
                        image_path.unlink()

                except OSError as error:
                    print("Error deleting image:", error)

        return len(expired_reports)

    def clear_temp_directory(self, temp_directory: str | Path) -> int:
        """_summary_
            Clears the temporary directory used for storing extracted files.
        Args:
            temp_directory (str | Path): The path to the temporary directory to be cleared.

        Returns:
            int: The number of files that were deleted. Returns 0 if the directory does not exist or if an error occurred.
        """
        temp_directory = Path(temp_directory)
        deleted_count = 0

        if not temp_directory.exists():
            return 0

        if not temp_directory.is_dir():
            print("Temporary path is not a directory")
            return 0

        try:
            for item in temp_directory.iterdir():
                if item.is_file():
                    try:
                        item.unlink()
                        deleted_count += 1

                    except OSError as error:
                        print("Error deleting temp file:", error)

        except OSError as error:
            print("Error accessing temporary directory:", error)

        return deleted_count
