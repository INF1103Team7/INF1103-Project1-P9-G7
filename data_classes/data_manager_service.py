import shutil
from pathlib import Path
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import os

from data_classes.data_report import Report
from data_classes.data_json_report_storage import JsonReportStorage

class DataManagerService:
    def __init__(self, reports_file, image_directory, temp_directory, image_extensions):
        # create the JSON storage object
        self._storage = JsonReportStorage(reports_file)
        # store the image directory path
        self._image_directory = image_directory
        self._image_extensions = image_extensions 
        self._temp_directory = temp_directory
    
    def load_reports(self):
        # load reports using the JSON storage object
        return self._storage.load_reports()
    
    def save_report_list(self, reports):
        # save reports using the JSON storage object
        return self._storage.save_reports(reports)
    
    def save_new_report(self, report_data):
        # create a Report object
        report = Report(report_data)
        # convert the report into a dictionary
        stored_report = report.to_dict()

        # check whether an image was provided
        source_path = stored_report.get("image_path")
        if source_path is not None:
            if not isinstance(source_path, str):
                raise ValueError("Image path must be a string")

            image_filename = self.store_image(
                source_path,
                report.get_case_id()
            )

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
    
    # Store an image in the images directory
    def store_image(self, source_path: str | Path, case_id: str) -> str:
        """_summary_
            Function to store an image in the images directory with a new filename based on the case ID.
        Args:
            source_path (str | Path): The path to the source image file to be stored.
            case_id (str): The case ID to be used for the new image filename.
            image_directory (Path, optional): The path to the image directory. Defaults to IMAGE_DIRECTORY.

        Raises:
            ValueError: If the source path is not a valid image file or if the case ID is not a string.
            FileNotFoundError: If the source image file is not found.

        Returns:
            str: The filename of the stored image.
        """
        # Load environment variables from .env file
        load_dotenv(Path(__file__).parent.parent / ".env")
        image_directory = Path(self._image_directory)
        source = Path(source_path)
        if source.suffix.lower() not in self._image_extensions:
            print("[!] Only JPG, JPEG, and PNG images can be stored.")
            return None
        if not source.is_file():
            print(f"[!] Image not found: {source}")
            return None

        image_directory.mkdir(parents=True, exist_ok=True)
        if image_directory == self._image_directory:
            stored_filename = f"{case_id}{source.suffix.lower()}"
            try:
                shutil.copy2(source, image_directory / stored_filename)
            except Exception as e:
                print(f"[!] Error saving file to database: {e}")
        elif image_directory == self._temp_directory:
            # Check if the application is running in a containerized environment
            if os.environ.get("APP_CONTAINER") == "1":
                try:
                    if str(source).find("/") != -1:
                        stored_filename = f"{str(source).split("/")[-1]}"
                    else:
                        stored_filename = f"{str(source).split('\\')[-1]}"
                    shutil.copy2(source, image_directory / stored_filename)
                except shutil.SameFileError:
                    print(f"[!] File already exists in the destination: {source} skipping copy.")
                except Exception as e:
                    print(f"[!] Error copying file: {e}")
            else:
                try:
                    stored_filename = f"{str(source).split("\\")[-1]}"
                    shutil.copy2(source, image_directory / stored_filename)
                except shutil.SameFileError:
                    print(f"[!] File already exists in the destination: {source} skipping copy.")
                except Exception as e:
                    print(f"[!] Error copying file: {e}")
        return stored_filename
        
    def get_active_reports(self):
        # store only reports with active status
        active_reports = []

        for report in self.load_reports():
            if report.get("status") == "active":
                active_reports.append(report)

        return active_reports

    def get_reports_by_category(self, category):
        # store reports matching the selected category
        matching_reports = []

        for report in self.get_active_reports():
            if report.get("category") == category:
                matching_reports.append(report)

        return matching_reports
    
    def get_report_by_id(self, case_id):
        # search for a report using its case ID
        for report in self.load_reports():
            if report.get("case_id") == case_id:
                return report

        return None

    def update_report_status(self, case_id, new_status):
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
    
    def delete_expired_reports(self, retention_days=30):
        if type(retention_days) is not int or retention_days < 0:
            raise ValueError("Retention days must be a non-negative integer")

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

    def clear_temp_directory(self, temp_directory):
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
