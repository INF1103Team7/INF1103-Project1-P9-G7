success.json
Tests normal AI outputs containing a mixture of strong, moderate, and weak matches.
1. RECOMMENDED_MATCH: Strong/complete match: color, material, brand, features and location all match
2. LOW_CONFIDENCE_MATCH: Weak match: only color supports it; material, brand and features don't match
3. match_failure: Very poor physical match: color, material, brand and features don't match

strong_match.json
Tests high-scoring reports with multiple matching attributes and positive business rules.
1. RECOMMENDED_MATCH: All major attributes + location match with high score
2. RECOMMENDED_MATCH: All major attributes + location match with high score
3. RECOMMENDED_MATCH: Brand, color, material and features match, but location doesn't


weak_match.json
Tests reports with poor physical similarity where the CORE_VISUAL_MISMATCH_VETO rule should trigger.
1. match_failure: Color + material don't match and zero features
2. match_failure: Same core visual mismatch condition
3. match_failure: Same core visual mismatch condition


multi_rule.json
Tests multiple business rules being triggered by the same report, including both positive and negative rules.
1. POTENTIAL_MATCH: Color + brand + features match, but material + location don't
2. RECOMMENDED_MATCH: Strong physical attributes match, but location doesn't
3. POTENTIAL_MATCH: Only color + location support the match; no brand/material/features


wrong_format.json
Tests invalid AI values such as an invalid similarity score, null color_match, and an invalid feature_overlap_match data type.
1. system_failure: Invalid similarity_score value: "not-a-score"
2. system_failure: Invalid/missing color_match: null
3. system_failure: Invalid feature_overlap_match: string instead of list

tie_score.json
Tests two reports with the same final score to verify how get_best_match() handles tied scores.
>> first two reports tie; will return first report

missing_keys.json
Tests missing and incorrectly named keys in similarity_analysis to verify that invalid AI structures are detected.
1. system_failure: Missing similarity_score key
2. POTENTIAL_MATCH: Missing material_match key
3. system_failure: Incorrectly named keys such as colour_match, material_mach, etc.