
from pathlib import Path

from data_classes.data_json_report_storage import JsonReportStorage


class DataManager:

    def __init__(self, reports_file, image_directory):
        # create the JSON storage object
        self._storage = JsonReportStorage(reports_file)
        # store the image directory path
        self._image_directory = Path(image_directory)
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

        # load existing reports
        reports = self.load_reports()

        # add the new report
        reports.append(stored_report)

        # save the updated report list
        if self.save_report_list(reports):
            return stored_report

        return None
    
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
