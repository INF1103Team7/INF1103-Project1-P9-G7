#found > io > ai > logic - pull from db via keys to send back ai; for loop to store in array > ai count score > logic > user

import json
from typing import Any, Dict, Union

# Track failure counts
system_failure_count = 0
match_failure_count = 0
total_failure_count = 0

# Threshold for AI similarity score below which a match is considered a failure
REJECT_THRESHOLD = 80

# 1 Get all records by category from database.py that match the specified category from the lost report description.
def get_reports_by_category(category):
    report_list = []
    try:
        with open("reports.json", "r") as f:
            reports = json.load(f)
            for report in reports:
                category_to_get = report.get("category")
                if category == category_to_get:
                    report_list.append(report)
    except FileNotFoundError:
        print("The file reports.json is not found!")
    except json.JSONDecodeError:
        print("Error: The file reports.json is corrupted!!")
    return report_list

# 2 Validate the AI result against business rules and record statuses.
def parse_score_to_float(score):
    if not isinstance(score, str):
        return "system_failure"
    if not score.endswith("%"):
        return "system_failure"
    
    try:
        ai_score = float(score[:-1])
        if not 0 <= ai_score <= 100:
            return "system_failure"
    except ValueError:
        return "system_failure"
    return ai_score
def validate_analysis(ai_result):
    if not isinstance(ai_result, dict):
        return "system_failure"
    similarity_score = ai_result.get("similarity_score")
    score_float = parse_score_to_float(similarity_score)
    if score_float == "system_failure":
        return "system_failure"
    elif score_float < REJECT_THRESHOLD:
        return "match_failure"
    
    return "valid"

# 3 Get top 5 matches
def get_top_matches(ai_result_list, limit=5):
    valid_reports_list = []

    for report in ai_result_list:
        result = validate_analysis(report)

        if result == "valid":
            valid_reports_list.append(report)

        elif result == "system_failure":
            update_failure_count("system_failure")

        elif result == "match_failure":
            update_failure_count("match_failure")

    valid_reports_list.sort(
        key=lambda x: float(
            x["similarity_analysis"]["similarity_score"].replace("%", "")
        ),
        reverse=True
    )

    top_reports = valid_reports_list[:limit]

    return top_reports

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