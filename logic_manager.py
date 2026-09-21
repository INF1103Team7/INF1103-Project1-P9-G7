#1 Validate similarity level and key features from AI json output
#2 Check false positive and false negative cases
#3 Similarity score above threshold
reject_threshold = 0.7
system_failure_count = 0
match_failure_count = 0
total_failure_count = 0
def validate_ai(similarity_level, key_features):
    if similarity_level is None or key_features is None:
        return "system_failure"
    if not isinstance(similarity_level, float):
        return "system_failure"
    if similarity_level < reject_threshold:
        return "match_failure"
    if not key_features:
        return "match_failure"
    return "valid"
def get_match(ai_result, lost_report, found_report):
    similarity_level = ai_result.get('similarity_level')
    key_features = ai_result.get('key_features')
    validation_result = validate_ai(similarity_level, key_features)
    if validation_result != "valid":
        return validation_result
    if lost_report["status"] == "resolved":
        return None
    if found_report["status"] == "resolved":
        return None
    return {
        "is_match": True,
        "lost_report_id": lost_report["report_id"],
        "found_report_id": found_report["report_id"],
        "similarity_level": similarity_level,
        "key_features": key_features
    }
results = get_match(ai_result, lost_report, found_report)
if results == "system_failure":
    system_failure_count += 1
    total_failure_count += 1
elif results == "match_failure":
    match_failure_count += 1
    total_failure_count += 1