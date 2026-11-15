
import math


FEATURE_FIELDS = [
    "Household_Size",
    "Bathing_Events",
    "Kitchen_Sessions",
    "Laundry_Loads",
    "Gardening_Duration_Minutes"
]

INTEGER_FIELDS = [
    "Household_Size",
    "Bathing_Events",
    "Kitchen_Sessions",
    "Laundry_Loads",
    "Gardening_Duration_Minutes"
]


def validate_household_input(data, require_budget=False):
    """
    Validate household activity inputs against the
    permitted synthetic training-data ranges.

    Returns:
        (validated_data, None) if valid
        (None, error_message) if invalid
    """

    if not isinstance(data, dict):
        return None, "Valid JSON input is required."

    required_fields = FEATURE_FIELDS.copy()

    if require_budget:
        required_fields.append("available_budget_liters")

    # 1. Check for missing fields
    for field in required_fields:
        if field not in data:
            return None, f"Missing required field: {field}."

    # 2. Check numeric values
    for field in required_fields:
        value = data[field]

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            return None, f"{field} must be a valid number."

    # 3. Check integer-only fields
    for field in INTEGER_FIELDS:
        if not isinstance(data[field], int):
            return None, f"{field} must be an integer."

    household_size = data["Household_Size"]
    bathing_events = data["Bathing_Events"]
    kitchen_sessions = data["Kitchen_Sessions"]
    laundry_loads = data["Laundry_Loads"]
    gardening_duration = data["Gardening_Duration_Minutes"]

    # 4. Household size
    if not 1 <= household_size <= 6:
        return None, "Household size must be an integer between 1 and 6."

    # 5. Bathing events
    if not 0 <= bathing_events <= household_size:
        return None, "Bathing events must be between 0 and household size."

    # 6. Kitchen sessions
    if not 2 <= kitchen_sessions <= 4:
        return None, "Kitchen sessions must be between 2 and 4."

    # 7. Laundry loads
    if not 0 <= laundry_loads <= 3:
        return None, "Laundry loads must be between 0 and 3."

    # 8. Gardening duration
    if gardening_duration != 0 and not 10 <= gardening_duration <= 60:
        return None, (
            "Gardening duration must be 0 or between 10 and 60 minutes."
        )

    # 9. Available water budget
    if require_budget:
        budget = data["available_budget_liters"]

        if budget <= 0:
            return None, "Available water budget must be greater than 0."

    return data, None
