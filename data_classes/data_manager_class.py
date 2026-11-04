
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