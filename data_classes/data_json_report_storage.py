from data_classes.data_report_storage import ReportStorage

class JsonReportStorage(ReportStorage):

    def __init__(self, file_path):
        super().__init__(file_path)
        
        # convert the file path into a Path object
        self._file_path = Path(file_path)
