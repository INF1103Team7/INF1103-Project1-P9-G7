import json
import os

DATA_FILE="data/reports.json"

def load_reports():
    if not os.paths.exists(DATA_FILE):
        return[]
    try:
        with open(DATA_FILE,"r") as file:
            reports= json.load(file)
        return reports
    except (json.JSONDecodeError,OSError):
        return []
    
