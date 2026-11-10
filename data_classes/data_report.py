# Report class

# Imports
from datetime import date
from uuid import uuid4


class Report:
    def __init__(self, report_data: dict):
        self._report_data = dict(report_data)
        # generate a caseID if one is not provided
        if not self._report_data.get("case_id"):
            self._report_data["case_id"] = self.create_case_id()
        
        # set "active" as default status
        if not self._report_data.get("status"):
            self._report_data["status"] = "active"

    def create_case_id(self) -> str:
        """_summary_
            Function to generate a unique case ID for a report. The case ID is formatted as "CASE-YYYYMMDD-XXXXXX", where "YYYYMMDD" is the current date and "XXXXXX" is a random 6-character alphanumeric string.
        Returns:
            str: A unique case ID for the report.
        """
        return f"CASE-{date.today():%Y%m%d}-{uuid4().hex[:6].upper()}"
    
    def get_case_id(self) -> str:
        """_summary_
            Function to retrieve the case ID of the report.
        Returns:
            str: The case ID of the report.
        """
        return self._report_data["case_id"]

    def get_category(self) -> str:
        """_summary_
            Function to retrieve the category of the report.
        Returns:
            str: The category of the report.
        """
        return self._report_data.get("category")

    def get_status(self) -> str:
        """_summary_
            Function to retrieve the status of the report.
        Returns:
            str: The status of the report.
        """
        return self._report_data["status"]
    
    def update_status(self, new_status: str) -> bool:
        """_summary_
            Updates the status of the report. The new status must be either "active" or "closed". If the status is updated to "closed", the current date is recorded as the closed date.
        Args:
            new_status (str): The new status to set for the report. Must be either "active" or "closed".

        Returns:
            bool: True if the status was successfully updated, False otherwise.
        """
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
    
    def to_dict(self) -> dict:
        """_summary_
            Function to convert the report object into a dictionary representation.
        Returns:
            dict: A dictionary containing the report data.
        """
        return dict(self._report_data)
