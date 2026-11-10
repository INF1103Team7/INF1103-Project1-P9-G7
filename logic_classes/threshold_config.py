# Manages the configuration of matching thresholds.
# Stores default threshold values and allows controlled updates through properties and validation methods.
class ThresholdConfig:
    # Class-level default constants for fallback assignments
    DEFAULT_REJECT_THRESHOLD = 50.0
    DEFAULT_HIGH_THRESHOLD = 80.0
    DEFAULT_MIN_FEATURE_STRONG_MATCH = 2
    DEFAULT_MIN_FEATURE_EXCELLENT_MATCH = 3
    DEFAULT_CONSIDER_LOCATION = True

    # Initialises the threshold configuration with default values.
    # Custom values can also be provided during object creation.
    def __init__(
        self,
        reject_threshold=50.0,
        high_threshold=80.0,
        min_feature_strong_match=2,
        min_feature_excellent_match=3,
    ):
        # Initialise default values first.
        self.__reject_threshold = self.DEFAULT_REJECT_THRESHOLD
        self.__high_threshold = self.DEFAULT_HIGH_THRESHOLD
        self.__min_feature_strong_match = (
            self.DEFAULT_MIN_FEATURE_STRONG_MATCH
        )
        self.__min_feature_excellent_match = (
            self.DEFAULT_MIN_FEATURE_EXCELLENT_MATCH
        )
        self.__consider_location = self.DEFAULT_CONSIDER_LOCATION

        # Use property setters to validate custom values.
        self.reject_threshold = reject_threshold
        self.high_threshold = high_threshold
        self.min_feature_strong_match = min_feature_strong_match
        self.min_feature_excellent_match = min_feature_excellent_match

    # Validates user input before allowing a threshold update.
    # Checks data type, minimum and maximum values, unchanged values, and relationships between lower and higher threshold boundaries.
    def __validate_input(
        self,
        value,
        current_value,
        data_type,
        min_value,
        max_value=None,
        lower_boundary=None,
        higher_boundary=None,
        lower_boundary_name="lower boundary",
        higher_boundary_name="higher boundary",
    ):
        # Reject boolean values because bool is a subclass of int in Python.
        if isinstance(value, bool):
            return False, "Invalid: Input must be numeric!!"

        try:
            # Convert the input to the required data type.
            # If an integer is required, reject decimal values.
            if (
                data_type is int
                and isinstance(value, float)
                and not value.is_integer()
            ):
                return False, "Invalid: Input must be a whole number!"

            value = data_type(value)

            # Check the minimum allowed value.
            if value < min_value:
                return False, f"Invalid: Input must be at least {min_value}"

            # Check the maximum allowed value, if one is provided.
            if max_value is not None and value > max_value:
                return False, f"Invalid: Input must not exceed {max_value}"

            # Ensure the higher boundary is greater than the lower boundary.
            if lower_boundary is not None and higher_boundary is not None:
                if higher_boundary <= lower_boundary:
                    return (
                        False,
                        (
                            f"Rejected: {higher_boundary_name} of"
                            f" {higher_boundary} must be greater than"
                            f" {lower_boundary_name} of {lower_boundary}"
                        ),
                    )
            # Return the validation result and converted value if all checks pass.
            return True, value

        except (ValueError, TypeError):
            # Handle inputs that cannot be converted to the required data type.
            return False, "Invalid: Input must be numeric!!"

    # Validates the new threshold value and returns the updated value.
    # Returns the default value if input fails validation instead of raising an error.
    def __update_threshold(
        self,
        value,
        current_value,
        data_type,
        min_value,
        max_value,
        lower_boundary,
        higher_boundary,
        lower_boundary_name,
        higher_boundary_name,
        default_value,
    ):
        is_valid, result = self.__validate_input(
            value,
            current_value,
            data_type,
            min_value,
            max_value,
            lower_boundary,
            higher_boundary,
            lower_boundary_name,
            higher_boundary_name,
        )

        if not is_valid:
            print(f"[!] {result} Using default value ({default_value}).")
            return default_value

        return result

    # Provides controlled access to private threshold attributes.
    # Property setters ensure that all updates pass through validation.

    @property
    def consider_location(self):
        return self.__consider_location

    @consider_location.setter
    def consider_location(self, value):
        if not isinstance(value, bool):
            print(
                "[!] Invalid Location Configuration!! Using default value"
                f" ({self.DEFAULT_CONSIDER_LOCATION})."
            )
            self.__consider_location = self.DEFAULT_CONSIDER_LOCATION
        else:
            self.__consider_location = value

    # Gets or updates the high confidence threshold.
    @property
    def high_threshold(self):
        return self.__high_threshold

    @high_threshold.setter
    def high_threshold(self, value):
        # The high threshold must be greater than the reject threshold.
        self.__high_threshold = self.__update_threshold(
            value,
            self.__high_threshold,
            float,
            0,
            100,
            self.__reject_threshold,
            value,
            "Reject threshold",
            "High threshold",
            self.DEFAULT_HIGH_THRESHOLD,
        )

    # Gets or updates the reject threshold.
    @property
    def reject_threshold(self):
        return self.__reject_threshold

    @reject_threshold.setter
    def reject_threshold(self, value):
        # The reject threshold must be lower than the high threshold.
        self.__reject_threshold = self.__update_threshold(
            value,
            self.__reject_threshold,
            float,
            0,
            100,
            value,
            self.__high_threshold,
            "Reject threshold",
            "High threshold",
            self.DEFAULT_REJECT_THRESHOLD,
        )

    # Gets or updates the minimum feature overlap required for a strong match.
    @property
    def min_feature_strong_match(self):
        return self.__min_feature_strong_match

    @min_feature_strong_match.setter
    def min_feature_strong_match(self, value):
        # The value must be lower than the excellent match threshold.
        self.__min_feature_strong_match = self.__update_threshold(
            value,
            self.__min_feature_strong_match,
            int,
            1,
            None,
            value,
            self.__min_feature_excellent_match,
            "Minimum feature overlap for strong match",
            "Minimum feature overlap for excellent match",
            self.DEFAULT_MIN_FEATURE_STRONG_MATCH,
        )

    # Gets or updates the minimum feature overlap required for an excellent match.
    @property
    def min_feature_excellent_match(self):
        return self.__min_feature_excellent_match

    @min_feature_excellent_match.setter
    def min_feature_excellent_match(self, value):
        # The value must be greater than the strong match threshold.
        self.__min_feature_excellent_match = self.__update_threshold(
            value,
            self.__min_feature_excellent_match,
            int,
            1,
            None,
            self.__min_feature_strong_match,
            value,
            "Minimum feature overlap for strong match",
            "Minimum feature overlap for excellent match",
            self.DEFAULT_MIN_FEATURE_EXCELLENT_MATCH,
        )