from datetime import date
from uuid import uuid4


class Report:

    def __init__(self, report_data):
        self._report_data = dict(report_data)
        # generate a caseID if one is not provided
        if not self._report_data.get("case_id"):
            self._report_data["case_id"] = self.create_case_id()

    def create_case_id(self):
        return f"CASE-{date.today():%Y%m%d}-{uuid4().hex[:6].upper()}"