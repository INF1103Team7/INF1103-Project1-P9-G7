from datetime import date
from uuid import uuid4


class Report:

    def __init__(self, report_data):
        self._report_data = dict(report_data)
