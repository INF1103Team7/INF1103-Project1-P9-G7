# Manage configurable thresholds for the business rules. This class encapsulates the threshold values and provides methods to update them with validation. #
class ThresholdConfig:
    def __init__(self):
        self.__reject_threshold = 50
        self.__high_threshold = 80
        self.__min_feature_strong_match = 2
        self.__min_feature_excellent_match = 3

    def __validate_input(
        self,
        value,
        current_value,
        data_type,
        min_value,
        max_value=None,
        lower_boundary=None,
        higher_boundary=None,
    ):
        # reject boolean values #
        if isinstance(value, bool):
            return False, "Invalid: Input must be numeric!!"
        try:
            # convert input to the required data type
            if data_type is int and isinstance(value, float) and not value.is_integer():
                return False, "Invalid: Input must be a whole number!"
            value = data_type(value)
            # check value change #
            if value == current_value:
                return False, "No change: Input is already set to this value."
            # check min value #
            if value < min_value:
                return False, f"Invalid: Input must be at least {min_value}"
            # check max value, if provided #
            if max_value is not None and value > max_value:
                return False, f"Invalid: Input must not exceed {max_value}"
            # check boundaries #
            if lower_boundary is not None and higher_boundary is not None:
                if higher_boundary <= lower_boundary:
                    return (
                        False,
                        f"Rejected: {higher_boundary} must be greater than {lower_boundary}",
                    )
            return True, value
        except (ValueError, TypeError):
            return False, "Invalid: Input must be numeric!!"
        
    def __update_threshold(
        self,
        value,
        current_value,
        data_type,
        min_value,
        max_value,
        lower_boundary,
        higher_boundary,
        attribute_name,
        success_message,
    ):
        is_valid, result = self.__validate_input(
            value,
            current_value,
            data_type,
            min_value,
            max_value,
            lower_boundary,
            higher_boundary,
        )

        if not is_valid:
            return result

        setattr(self, attribute_name, result)
        return success_message.format(value=result)
    def update_high_threshold(self, value):
        return self.__update_threshold(
            value,
            self.__high_threshold,
            float,
            0,
            100,
            self.__reject_threshold,
            value,
            "_ThresholdConfig__high_threshold",
            "Successful update: High threshold is now {value}",
        )
    def update_reject_threshold(self, value):
        return self.__update_threshold(
            value,
            self.__reject_threshold,
            float,
            0,
            100,
            value,
            self.__high_threshold,
            "_ThresholdConfig__reject_threshold",
            "Successful update: Reject threshold is now {value}",
        )
    def update_min_feature_strong_match(self, value):
        return self.__update_threshold(
            value,
            self.__min_feature_strong_match,
            int,
            1,
            None,
            value,
            self.__min_feature_excellent_match,
            "_ThresholdConfig__min_feature_strong_match",
            "Successful update: Minimum feature overlap for strong match is now {value}",
        )
    def update_min_feature_excellent_match(self, value):
        return self.__update_threshold(
            value,
            self.__min_feature_excellent_match,
            int,
            1,
            None,
            self.__min_feature_strong_match,
            value,
            "_ThresholdConfig__min_feature_excellent_match",
            "Successful update: Minimum feature overlap for excellent match is now {value}",
        )
    def get_reject_threshold(self):
        return self.__reject_threshold

    def get_high_threshold(self):
        return self.__high_threshold

    def get_min_feature_strong_match(self):
        return self.__min_feature_strong_match

    def get_min_feature_excellent_match(self):
        return self.__min_feature_excellent_match

    def reset_all_threshold(self):
        self.__reject_threshold = 50
        self.__high_threshold = 80
        self.__min_feature_strong_match = 2
        self.__min_feature_excellent_match = 3
        return "All 4 thresholds successfully reset to default values."
