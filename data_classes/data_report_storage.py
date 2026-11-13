# data report storage abstract class

from abc import ABC, abstractmethod


class ReportStorage(ABC):
    def __init__(self, file_path):
        #store file path for report storage
        self._file_path = file_path
    
    @abstractmethod
    def load_reports(self):
        # child classes must implement report loading
        pass
       
    @abstractmethod
    def save_reports(self, reports):
        # child classes must implement report saving
        pass