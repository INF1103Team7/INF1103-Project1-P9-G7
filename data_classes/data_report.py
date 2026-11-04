from datetime import date
from uuid import uuid4


class Report:

    def __init__(self, report_data):
        self._report_data = dict(report_data)
        # generate a caseID if one is not provided
        if not self._report_data.get("case_id"):
            self._report_data["case_id"] = self.create_case_id()
        
        # set "active" as default status
        if not self._report_data.get("status"):
            self._report_data["status"] = "active"

    def create_case_id(self):
        return f"CASE-{date.today():%Y%m%d}-{uuid4().hex[:6].upper()}"
    
    def get_category(self):
        return self._report_data.get("category")

    def get_status(self):
        return self._report_data["status"]
    
    def update_status(self, new_status):
        # check that the new status is a string
        if not isinstance(new_status, str):
            return False

        new_status = new_status.lower()

        # only allow if status is active or closed
        if new_status not in ["active", "closed"]:
            return False

        self._report_data["status"] = new_status

        # record the date when a report is closed
        if new_status == "closed":
            self._report_data["closed_date"] = date.today().isoformat()
        else:
            self._report_data.pop("closed_date", None)

        return True
  