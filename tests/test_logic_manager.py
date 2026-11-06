import pytest

from logic_manager import LogicManager

from logic_classes.analysis_validator import AnalysisValidator
from logic_classes.match_rule import MatchRule
from logic_classes.match_selector import MatchSelector
from logic_classes.matcher import Matcher
from logic_classes.rule_manager import RuleManager
from logic_classes.threshold_config import ThresholdConfig
from logic_classes.traits import Traits


# ============================================================
# SHARED TEST DATA
# ============================================================

@pytest.fixture
def valid_ai_result():
    return {
        "date": "25-09-2026",
        "similarity_analysis": {
            "similarity_score": 85,
            "color_match": {
                "is_match": "match",
                "primary": "black",
                "secondary": "white"
            },
            "material_match": "match",
            "brand_match": "match",
            "location_match": "match",
            "feature_overlap_match": [
                "black flex cap with handle",
                "Hydro Flask logo"
            ]
        }
    }


@pytest.fixture
def validator():
    return AnalysisValidator()


@pytest.fixture
def config():
    return ThresholdConfig()


@pytest.fixture
def traits():
    return Traits()


@pytest.fixture
def matcher():
    return Matcher()


@pytest.fixture
def rule_manager():
    return RuleManager(ThresholdConfig())

def create_empty_rule_manager():
    manager = RuleManager(ThresholdConfig())

    manager.veto_rules.clear()
    manager.negative_rules.clear()
    manager.positive_rules.clear()
    manager.bonus_rules.clear()

    return manager
# ============================================================
# 1. ANALYSIS VALIDATOR TESTS
# ============================================================

def test_validator_accepts_valid_ai_result(validator, valid_ai_result):
    status, score = validator.validate_analysis(valid_ai_result)

    assert status == "valid"
    assert score == 85.0


@pytest.mark.parametrize(
    "score",
    [85, 85.5, "85", "85%", " 85% "]
)
def test_validator_accepts_valid_score_formats(
    validator, valid_ai_result, score
):
    valid_ai_result["similarity_analysis"]["similarity_score"] = score

    status, result = validator.validate_analysis(valid_ai_result)

    assert status == "valid"
    assert isinstance(result, float)


@pytest.mark.parametrize(
    "score",
    [True, False, -1, 101, "invalid", None, ""]
)
def test_validator_rejects_invalid_scores(
    validator, valid_ai_result, score
):
    valid_ai_result["similarity_analysis"]["similarity_score"] = score

    status, message = validator.validate_analysis(valid_ai_result)

    assert status == "system_failure"
    assert message is not None


def test_validator_rejects_non_dictionary_input(validator):
    status, message = validator.validate_analysis("invalid")

    assert status == "system_failure"


def test_validator_rejects_missing_similarity_analysis(validator):
    status, message = validator.validate_analysis({
        "date": "25-09-2026"
    })

    assert status == "system_failure"


def test_validator_rejects_invalid_color_match(
    validator, valid_ai_result
):
    valid_ai_result["similarity_analysis"]["color_match"] = "unknown"

    status, message = validator.validate_analysis(valid_ai_result)

    assert status == "system_failure"


def test_validator_rejects_invalid_feature_list(
    validator, valid_ai_result
):
    valid_ai_result["similarity_analysis"]["feature_overlap_match"] = "logo"

    status, message = validator.validate_analysis(valid_ai_result)

    assert status == "system_failure"


def test_validator_accepts_valid_timeline(
    validator, valid_ai_result
):
    result = validator.validate_timeline(
        valid_ai_result,
        "24-09-2026"
    )

    assert result == "valid"


def test_validator_detects_impossible_timeline(
    validator, valid_ai_result
):
    valid_ai_result["date"] = "23-09-2026"

    result = validator.validate_timeline(
        valid_ai_result,
        "24-09-2026"
    )

    assert result == "impossible_timeline"


def test_validator_returns_unknown_for_invalid_date(
    validator, valid_ai_result
):
    valid_ai_result["date"] = "invalid-date"

    result = validator.validate_timeline(
        valid_ai_result,
        "24-09-2026"
    )

    assert result == "unknown"


def test_validator_returns_unknown_when_lost_date_is_missing(
    validator, valid_ai_result
):
    result = validator.validate_timeline(
        valid_ai_result,
        None
    )

    assert result == "unknown"


# ============================================================
# 2. THRESHOLD CONFIGURATION TESTS
# ============================================================

def test_threshold_config_default_values(config):
    assert config.reject_threshold == 50.0
    assert config.high_threshold == 80.0
    assert config.min_feature_strong_match == 2
    assert config.min_feature_excellent_match == 3
    assert config.consider_location is True


def test_threshold_config_accepts_valid_custom_values():
    config = ThresholdConfig(
        reject_threshold=40,
        high_threshold=90,
        min_feature_strong_match=2,
        min_feature_excellent_match=4
    )

    assert config.reject_threshold == 40
    assert config.high_threshold == 90
    assert config.min_feature_strong_match == 2
    assert config.min_feature_excellent_match == 4


@pytest.mark.parametrize("value", [True, False])
def test_threshold_config_rejects_boolean_high_threshold(config, value):
    with pytest.raises(ValueError):
        config.high_threshold = value


def test_threshold_config_rejects_high_threshold_above_100(config):
    with pytest.raises(ValueError):
        config.high_threshold = 101


def test_threshold_config_rejects_negative_reject_threshold(config):
    with pytest.raises(ValueError):
        config.reject_threshold = -1


def test_threshold_config_rejects_high_threshold_below_reject(config):
    with pytest.raises(ValueError):
        config.high_threshold = 40


def test_threshold_config_rejects_reject_threshold_above_high(config):
    with pytest.raises(ValueError):
        config.reject_threshold = 90


def test_threshold_config_rejects_decimal_feature_count(config):
    with pytest.raises(ValueError):
        config.min_feature_strong_match = 2.5


def test_threshold_config_rejects_boolean_feature_count(config):
    with pytest.raises(ValueError):
        config.min_feature_strong_match = True


def test_threshold_config_rejects_strong_feature_count_not_below_excellent(
    config
):
    with pytest.raises(ValueError):
        config.min_feature_strong_match = 3


def test_threshold_config_rejects_excellent_feature_count_not_above_strong(
    config
):
    with pytest.raises(ValueError):
        config.min_feature_excellent_match = 2


def test_threshold_config_accepts_valid_threshold_updates(config):
    config.reject_threshold = 45
    config.high_threshold = 85

    assert config.reject_threshold == 45
    assert config.high_threshold == 85


def test_threshold_config_accepts_valid_feature_updates(config):
    config.min_feature_excellent_match = 4
    config.min_feature_strong_match = 3

    assert config.min_feature_strong_match == 3
    assert config.min_feature_excellent_match == 4


def test_threshold_config_accepts_same_existing_value(config):
    config.high_threshold = 80.0
    config.reject_threshold = 50.0

    assert config.high_threshold == 80.0
    assert config.reject_threshold == 50.0


def test_threshold_config_consider_location_accepts_boolean(config):
    config.consider_location = False

    assert config.consider_location is False

    config.consider_location = True

    assert config.consider_location is True


def test_threshold_config_consider_location_rejects_non_boolean(config):
    with pytest.raises(ValueError):
        config.consider_location = "False"


# ============================================================
# 3. TRAITS TESTS
# ============================================================

def test_traits_extracts_matching_attributes(
    traits, valid_ai_result
):
    result = traits.get_traits(
        valid_ai_result,
        "24-09-2026"
    )

    assert result["color_match"] == "match"
    assert result["material_match"] == "match"
    assert result["brand_match"] == "match"
    assert result["location_match"] == "match"
    assert len(result["feature_overlaps"]) == 2
    assert result["time_match"] == "valid"


def test_traits_extracts_non_matching_attributes(traits):
    ai_result = {
        "date": "25-09-2026",
        "similarity_analysis": {
            "similarity_score": 60,
            "color_match": "not match",
            "material_match": "not match",
            "brand_match": "not match",
            "location_match": "not match",
            "feature_overlap_match": []
        }
    }

    result = traits.get_traits(
        ai_result,
        "24-09-2026"
    )

    assert result["color_match"] == "not match"
    assert result["material_match"] == "not match"
    assert result["brand_match"] == "not match"
    assert result["location_match"] == "not match"
    assert result["feature_overlaps"] == []


def test_traits_classifies_matched_and_mismatched_attributes(
    traits, valid_ai_result
):
    data = traits.get_traits(
        valid_ai_result,
        "24-09-2026"
    )

    matched, mismatched = traits.classify_traits(data)

    assert "color" in matched
    assert "material" in matched
    assert "brand" in matched
    assert "location" in matched
    assert mismatched == []


# ============================================================
# 4. RULE MANAGER TESTS
# ============================================================

class DummyRule(MatchRule):
    """A simple rule used to test RuleManager behaviour."""

    def __init__(
        self,
        name,
        rule_type,
        satisfied=True,
        score_change=0,
        skip_after_veto=False
    ):
        self.name = name
        self.rule_type = rule_type
        self.satisfied = satisfied
        self.score_change = score_change
        self.skip_after_veto = skip_after_veto

    def is_satisfied(self, data):
        return self.satisfied

    def apply_rule(self, score):
        return score + self.score_change

    def get_rule_name(self):
        return self.name

    def get_rule_type(self):
        return self.rule_type

    def skip_if_veto_triggered(self):
        return self.skip_after_veto


def test_rule_manager_registers_default_rules(rule_manager):
    assert len(rule_manager.veto_rules) > 0
    assert len(rule_manager.negative_rules) > 0
    assert len(rule_manager.positive_rules) > 0
    assert len(rule_manager.bonus_rules) > 0


def test_rule_manager_rejects_invalid_rule_type(rule_manager):
    invalid_rule = DummyRule(
        "INVALID_RULE",
        "invalid"
    )

    with pytest.raises(ValueError):
        rule_manager.add_rule(invalid_rule)


def test_rule_manager_applies_positive_rule_once():
    manager = create_empty_rule_manager()

    manager.add_rule(
        DummyRule("POSITIVE_ONE", "positive", True, 10)
    )
    manager.add_rule(
        DummyRule("POSITIVE_TWO", "positive", True, 20)
    )

    result = manager.evaluate({}, 50)

    assert result["final_score"] == 60
    assert result["positive_rule"] == "POSITIVE_ONE"


def test_rule_manager_applies_bonus_rules():
    manager = create_empty_rule_manager()

    manager.add_rule(
        DummyRule("BONUS_ONE", "bonus", True, 5)
    )
    manager.add_rule(
        DummyRule("BONUS_TWO", "bonus", True, 3)
    )

    result = manager.evaluate({}, 50)

    assert result["final_score"] == 58


def test_rule_manager_clamps_score_to_100():
    manager = create_empty_rule_manager()

    manager.add_rule(
        DummyRule("BONUS", "bonus", True, 30)
    )

    result = manager.evaluate({}, 90)

    assert result["final_score"] == 100


def test_rule_manager_clamps_score_to_zero():
    manager = create_empty_rule_manager()

    manager.add_rule(
        DummyRule("NEGATIVE", "negative", True, -30)
    )

    result = manager.evaluate({}, 10)

    assert result["final_score"] == 0


def test_rule_manager_applies_veto_rule():
    manager = create_empty_rule_manager()

    manager.add_rule(
        DummyRule("TEST_VETO", "veto", True, 0)
    )

    result = manager.evaluate({}, 80)

    assert result["veto_triggered"] is True


def test_rule_manager_skips_negative_rule_after_veto():
    manager = create_empty_rule_manager()

    manager.add_rule(
        DummyRule("TEST_VETO", "veto", True, 0)
    )
    manager.add_rule(
        DummyRule(
            "SKIPPED_NEGATIVE",
            "negative",
            True,
            -20,
            skip_after_veto=True
        )
    )

    result = manager.evaluate({}, 80)

    assert "SKIPPED_NEGATIVE" not in result["triggered_rules_list"]


# ============================================================
# 5. MATCHER TESTS
# ============================================================

def test_matcher_returns_system_failure_for_invalid_input(matcher):
    result = matcher.evaluate_analysis(
        {"invalid": "data"},
        "24-09-2026"
    )

    assert result["status"] == "system_failure"


def test_matcher_detects_temporal_paradox(
    matcher, valid_ai_result
):
    valid_ai_result["date"] = "23-09-2026"

    result = matcher.evaluate_analysis(
        valid_ai_result,
        "24-09-2026"
    )

    assert result["status"] == "match_failure"
    assert result["final_composite_score"] == 0
    assert "TEMPORAL_PARADOX_VETO" in result["triggered_rules_list"]


def test_matcher_evaluates_valid_result(
    matcher, valid_ai_result
):
    result = matcher.evaluate_analysis(
        valid_ai_result,
        "24-09-2026"
    )

    assert result["status"] in [
        "RECOMMENDED_MATCH",
        "POTENTIAL_MATCH",
        "LOW_CONFIDENCE_MATCH"
    ]

    assert isinstance(result["final_composite_score"], (int, float))
    assert 0 <= result["final_composite_score"] <= 100


def test_matcher_returns_recommended_match_for_strong_match(
    matcher, valid_ai_result
):
    result = matcher.evaluate_analysis(
        valid_ai_result,
        "24-09-2026"
    )

    assert result["status"] == "RECOMMENDED_MATCH"


def test_matcher_returns_low_confidence_for_low_score(matcher):
    ai_result = {
        "date": "25-09-2026",
        "similarity_analysis": {
            "similarity_score": 10,
            "color_match": "match",
            "material_match": "not match",
            "brand_match": "not match",
            "location_match": "not match",
            "feature_overlap_match": []
        }
    }

    result = matcher.evaluate_analysis(
        ai_result,
        "24-09-2026"
    )

    assert result["status"] == "LOW_CONFIDENCE_MATCH"


# ============================================================
# 6. MATCH SELECTOR TESTS
# ============================================================

def test_match_selector_returns_none_for_empty_list():
    selector = MatchSelector()

    result = selector.get_best_match([])

    assert result is None


def test_match_selector_selects_highest_priority():
    selector = MatchSelector()

    results = [
        {
            "report": "Report A",
            "evaluation": {
                "status": "POTENTIAL_MATCH",
                "final_composite_score": 95
            }
        },
        {
            "report": "Report B",
            "evaluation": {
                "status": "RECOMMENDED_MATCH",
                "final_composite_score": 80
            }
        }
    ]

    result = selector.get_best_match(results)

    assert result["report"] == "Report B"


def test_match_selector_uses_score_when_priority_is_equal():
    selector = MatchSelector()

    results = [
        {
            "report": "Report A",
            "evaluation": {
                "status": "POTENTIAL_MATCH",
                "final_composite_score": 70
            }
        },
        {
            "report": "Report B",
            "evaluation": {
                "status": "POTENTIAL_MATCH",
                "final_composite_score": 90
            }
        }
    ]

    result = selector.get_best_match(results)

    assert result["report"] == "Report B"


def test_match_selector_skips_failed_evaluations():
    selector = MatchSelector()

    results = [
        {
            "report": "Report A",
            "evaluation": {
                "status": "system_failure",
                "final_composite_score": 100
            }
        },
        {
            "report": "Report B",
            "evaluation": {
                "status": "match_failure",
                "final_composite_score": 100
            }
        }
    ]

    result = selector.get_best_match(results)

    assert result is None


# ============================================================
# 7. LOGIC MANAGER TESTS
# ============================================================

def test_logic_manager_returns_none_for_empty_input():
    manager = LogicManager()

    result = manager.get_best_match(
        [],
        lost_report_date="24-09-2026"
    )

    assert result is None


def test_logic_manager_can_receive_custom_threshold_config():
    config = ThresholdConfig()
    manager = LogicManager(threshold_config=config)

    assert manager.matcher.threshold_config is config