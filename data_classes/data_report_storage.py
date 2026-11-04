
class ReportStorage:

    def __init__(self, file_path):
        self._file_path = file_path
        
    def load_reports(self):
        raise NotImplementedError("Subclasses must implement load_reports")
       
    def save_reports(self, reports):
        raise NotImplementedError("Subclasses must implement save_reports")