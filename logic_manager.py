REJECT_THRESHOLD = 0.7

system_failure_count = 0
match_failure_count = 0
total_failure_count = 0

def validate_ai(ai_result):
    # AI result must be a dictionary
    if not isinstance(ai_result, dict):
        return "system_failure"

    similarity_level = ai_result.get("similarity_level")
    key_features = ai_result.get("key_features")

    # Required fields must exist
    if similarity_level is None or key_features is None:
        return "system_failure"

    # Similarity level must be a number
    if not isinstance(similarity_level, (int, float)):
        return "system_failure"

    # Similarity level must be between 0 and 1
    if not 0 <= similarity_level <= 1:
        return "system_failure"

    # Similarity score below threshold is not considered a match
    if similarity_level < REJECT_THRESHOLD:
        return "match_failure"

    # There must be at least one matching feature
    if not key_features:
        return "match_failure"

    return "valid"


def check_report_status(report):
    if not isinstance(report, dict):
        return False

    return report.get("status") != "resolved"

def get_match(ai_result, lost_report, found_report):
    # Validate the reports
    if not isinstance(lost_report, dict):
        return "system_failure"

    if not isinstance(found_report, dict):
        return "system_failure"

    # Do not match reports that have already been resolved
    if not check_report_status(lost_report):
        return None

    if not check_report_status(found_report):
        return None

    # Validate the AI result
    validation_result = validate_ai(ai_result)

    if validation_result != "valid":
        return validation_result

    similarity_level = ai_result.get("similarity_level")
    key_features = ai_result.get("key_features")

    # Use the current project's case_id instead of the old report_id
    lost_case_id = lost_report.get("case_id")
    found_case_id = found_report.get("case_id")

    # case_id is required for identifying reports
    if lost_case_id is None or found_case_id is None:
        return "system_failure"

    return {
        "is_match": True,
        "lost_case_id": lost_case_id,
        "found_case_id": found_case_id,
        "similarity_level": similarity_level,
        "key_features": key_features,
    }

def update_failure_counts(result):
    global system_failure_count
    global match_failure_count
    global total_failure_count

    if result == "system_failure":
        system_failure_count += 1
        total_failure_count += 1

    elif result == "match_failure":
        match_failure_count += 1
        total_failure_count += 1

def get_failure_counts():
    return {
        "system_failure_count": system_failure_count,
        "match_failure_count": match_failure_count,
        "total_failure_count": total_failure_count,
    }