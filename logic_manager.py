#found > io > ai > logic - pull from db via keys to send back ai; for loop to store in array > ai count score > logic > user
'''
category = desc["category"]
store = []
with open("reports.json", "r") as f:
    content = f.read()
for data in content:
    if category:
        store.append(data)

'''
import json
from typing import Any, Dict, Union

# Track failure counts
system_failure_count = 0
match_failure_count = 0
total_failure_count = 0

# Threshold for AI similarity score below which a match is considered a failure
REJECT_THRESHOLD = 0.8

# 1 Get all records by category from database.py that match the specified category from the lost report description.
def get_items_by_category(category):
    item_list = []
    try:
        with open("reports.json", "r") as f:
            content = json.load(f)
            for data in content:
                category_to_get = data.get("category","").strip().lower()
                if category == category_to_get:
                    item_list.append(data)
    except FileNotFoundError:
        print("The file reports.json is not found!")
    except json.JSONDecodeError:
        print("Error: The file reports.json is corrupted!!")
    return item_list

# 2 Validate the AI result against business rules and record statuses.
def validate_ai(ai_result):
    if not isinstance(ai_result, dict):
        return "system_failure"
    similarity_level = ai_result.get("similarity_level")
    key_features = ai_result.get("key_features")
    if similarity_level is None or key_features is None:
        return "system_failure"
    if not isinstance(similarity_level, (int, float)):
        return "system_failure"
    if not 0.0 <= float(similarity_level) <= 1.0:
        return "system_failure"
    if similarity_level < REJECT_THRESHOLD:
        return "match_failure"
    if not key_features:
        return "match_failure"

    return "valid"

# 3 Get top 5 matches
def get_top_matches(ai_result_list, limit = 5):
    valid_reports = []
    for result in ai_result_list:
        report_status = validate_ai(result)
        if report_status != "valid":
            update_failure_count(report_status)
            continue
        valid_reports.append(result)
    top_matches = sorted(valid_reports, key=lambda x: x["similarity_level"], reverse=True)[:limit]
    return top_matches

# 4 Return top 5 matches records to send to io_manager.py
def fetch_full_report(top_matches):
    if not top_matches:
        return []
    try:
        with open("reports.json", "r") as f:
            content = json.load(f)
        get_report_by_id = {report["case_id"]: report for report in content if "case_id" in report}
    except FileNotFoundError:
        print("The file reports.json is not found!")
        return []
    except json.JSONDecodeError:
        print("Error: The file reports.json is corrupted!!")
        return []
    full_report_list = []
    for match in top_matches:
        case_id = match.get("case_id")
        if case_id in get_report_by_id:
            full_report = get_report_by_id[case_id].copy()
            full_report["similarity_level"] = match["similarity_level"]
            full_report["key_features_matched"] = match["key_features"]
            full_report_list.append(full_report)
    return full_report_list

# Update failure counts based on the result of the match evaluation
def update_failure_count(result):
    global system_failure_count
    global match_failure_count
    global total_failure_count

    if result == "system_failure":
        system_failure_count += 1
        total_failure_count += 1
    elif result == "match_failure":
        match_failure_count += 1
        total_failure_count += 1

# Save failure counts to a JSON file
def save_failure_count():
    global system_failure_count
    global match_failure_count
    global total_failure_count
    
    save_counts = {
        "system_failure_count": system_failure_count,
        "match_failure_count": match_failure_count,
        "total_failure_count": total_failure_count,
    }
    with open("failure_counts.json", "w") as f:
        json.dump(save_counts, f, indent=4)
        print("Failure counts saved to failure_counts.json")

# Load failure counts from a JSON file
def load_failure_count():
    global system_failure_count
    global match_failure_count
    global total_failure_count
    
    try:
        with open("failure_counts.json", "r") as f:
            counts = json.load(f)
            system_failure_count = counts.get("system_failure_count", 0)
            match_failure_count = counts.get("match_failure_count", 0)
            total_failure_count = counts.get("total_failure_count", 0)
            print("Failure counts loaded from failure_counts.json")
    except FileNotFoundError:
        print("No existing failure counts found. Counters all start from 0.")