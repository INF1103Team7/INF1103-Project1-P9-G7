from data_classes.data_report_storage import ReportStorage

class JsonReportStorage(ReportStorage):

    def __init__(self, file_path):
        super().__init__(file_path)
        
        # convert the file path into a Path object
        self._file_path = Path(file_path)
        
    def load_reports(self):
        # return an empty list if the file does not exist
        if not self._file_path.is_file():
            return []

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

    
    