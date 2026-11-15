
ACTIVITY_RECOMMENDATIONS = {
    "bathroom": {
        "title": "Reduce bathroom water usage",
        "actions": [
            "Prefer bucket baths or shorter showers.",
            "Turn off taps while brushing or applying soap.",
            "Check taps and bathroom fixtures for leakage.",
            "Install water-efficient showerheads where possible."
        ]
    },
    "kitchen": {
        "title": "Use kitchen water efficiently",
        "actions": [
            "Wash vegetables and utensils in a partially filled basin.",
            "Avoid keeping the tap running unnecessarily.",
            "Reuse suitable vegetable-washing water for plants.",
            "Repair leaking kitchen taps."
        ]
    },
    "laundry": {
        "title": "Optimize laundry water usage",
        "actions": [
            "Run the washing machine with reasonably full loads.",
            "Select the water level according to the laundry load.",
            "Avoid unnecessary repeat washing.",
            "Reuse rinse water for appropriate cleaning tasks when safe."
        ]
    },
    "gardening": {
        "title": "Reduce gardening water usage",
        "actions": [
            "Water plants during early morning or evening.",
            "Use a watering can or drip irrigation instead of a running hose.",
            "Apply mulch to reduce evaporation from soil.",
            "Reuse suitable non-contaminated household water for plants."
        ]
    }
}


def generate_conservation_recommendations(optimization_result):
    """
    Generate practical conservation suggestions from
    the output of the water allocation optimizer.
    """

    if not isinstance(optimization_result, dict):
        raise ValueError("Optimization result must be a dictionary.")

    if not optimization_result.get("success"):
        return {
            "status": "infeasible",
            "message": (
                "The available water budget is below the minimum "
                "required allocation. Increase the budget before "
                "generating an allocation-based conservation plan."
            ),
            "recommendations": []
        }

    allocations = optimization_result.get("activity_allocations")

    if not isinstance(allocations, dict):
        raise ValueError("Activity allocation data is missing.")

    recommendations = []

    for activity, details in allocations.items():

        if activity not in ACTIVITY_RECOMMENDATIONS:
            continue

        if not isinstance(details, dict):
            continue

        predicted = float(details.get("predicted_liters", 0))
        optimized = float(details.get("optimized_liters", 0))
        reduction = float(details.get("water_reduced_liters", 0))

        if reduction <= 0.01:
            continue

        reduction_percentage = (
            reduction / predicted * 100
            if predicted > 0 else 0
        )

        if reduction_percentage >= 20:
            priority = "High"
        elif reduction_percentage >= 10:
            priority = "Medium"
        else:
            priority = "Low"

        activity_data = ACTIVITY_RECOMMENDATIONS[activity]

        recommendations.append({
            "activity": activity,
            "title": activity_data["title"],
            "priority": priority,
            "predicted_liters": round(predicted, 2),
            "optimized_liters": round(optimized, 2),
            "target_reduction_liters": round(reduction, 2),
            "target_reduction_percentage": round(
                reduction_percentage, 2
            ),
            "actions": activity_data["actions"]
        })

    recommendations.sort(
        key=lambda item: item["target_reduction_liters"],
        reverse=True
    )

    if recommendations:
        message = (
            "Conservation recommendations generated successfully."
        )
    else:
        message = (
            "The optimizer did not identify any activity-wise "
            "allocation reductions for this water budget."
        )

    return {
        "status": "success",
        "message": message,
        "recommendations": recommendations,
        "disclaimer": (
            "These are practical suggestions based on optimized "
            "allocation targets. Actual water savings depend on "
            "household behaviour and implementation."
        )
    }
