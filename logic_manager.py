from typing import Any, Dict, Union
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
    if not 0.0 <= float(similarity_level) <= 1.0:
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

def get_match(
    lost_report: Dict[str, Any], 
    found_report: Dict[str, Any],
    ai_result: Dict[str, Any]
) -> Union[str, Dict[str, Any], None]:
    """
    Evaluates an AI matching result against business rules and record statuses.
    """
    # 1. System Input Integrity Gates
    if not isinstance(lost_report, dict) or not isinstance(found_report, dict):
        update_failure_counts("system_failure")
        return "system_failure"

    # 2. Lifecycle Status Gate: Do not match closed, claimed, or returned items
    if not is_report_active(lost_report) or not is_report_active(found_report):
        return None

    # 3. AI Result Business Verification Gate
    validation_result = validate_ai(ai_result)
    if validation_result != "valid":
        update_failure_counts(validation_result)
        return validation_result

    # 4. Identification Requirements Gate
    lost_case_id = lost_report.get("case_id")
    found_case_id = found_report.get("case_id")

    if not lost_case_id or not found_case_id:
        update_failure_counts("system_failure")
        return "system_failure"

    # Return valid match confirmation payload
    return {
        "is_match": True,
        "lost_case_id": lost_case_id,
        "found_case_id": found_case_id,
        "similarity_level": ai_result.get("similarity_level"),
        "key_features": ai_result.get("key_features"),
    }


def update_failure_counts(result: str) -> None:
    """Updates operational state performance logs based on failure classifications."""
    global system_failure_count
    global match_failure_count
    global total_failure_count

    if result == "system_failure":
        system_failure_count += 1
        total_failure_count += 1
    elif result == "match_failure":
        match_failure_count += 1
        total_failure_count += 1


def get_failure_counts() -> Dict[str, int]:
    """Retrieves standard metrics data mapping for application monitoring."""
    return {
        "system_failure_count": system_failure_count,
        "match_failure_count": match_failure_count,
        "total_failure_count": total_failure_count,
    }