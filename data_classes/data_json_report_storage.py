from data_classes.data_report_storage import ReportStorage

class JsonReportStorage(ReportStorage):

    def __init__(self, file_path):
        super().__init__(file_path)
