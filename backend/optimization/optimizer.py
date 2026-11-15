
from scipy.optimize import linprog
import math


# Activities used by the KNN prediction model
ACTIVITIES = [
    "bathroom",
    "kitchen",
    "laundry",
    "gardening"
]


# Minimum permitted allocation as a fraction of predicted demand
MINIMUM_RATIOS = {
    "bathroom": 0.80,
    "kitchen": 0.90,
    "laundry": 0.60,
    "gardening": 0.40
}


# Higher weight = higher allocation priority
PRIORITY_WEIGHTS = {
    "bathroom": 4,
    "kitchen": 5,
    "laundry": 3,
    "gardening": 1
}


def optimize_water_allocation(predicted_demand, available_budget):
    """
    Optimize daily water allocation across household activities.

    Parameters:
        predicted_demand (dict): Predicted litres for each activity.
        available_budget (float): Total available daily water in litres.

    Returns:
        dict: Optimization status, allocations, and potential savings.
    """

    # 1. Validate the predicted demand
    if not isinstance(predicted_demand, dict):
        raise ValueError("Predicted demand must be a dictionary.")

    for activity in ACTIVITIES:
        if activity not in predicted_demand:
            raise ValueError(
                f"Missing predicted demand for {activity}."
            )

        value = predicted_demand[activity]

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError(
                f"Demand for {activity} must be a non-negative number."
            )

    # 2. Validate the available water budget
    if (
        isinstance(available_budget, bool)
        or not isinstance(available_budget, (int, float))
        or not math.isfinite(available_budget)
        or available_budget < 0
    ):
        raise ValueError(
            "Available water budget must be a non-negative number."
        )

    # 3. Prepare demand, lower bounds, and priority weights
    demand = [float(predicted_demand[a]) for a in ACTIVITIES]

    minimum_allocation = [
        demand[i] * MINIMUM_RATIOS[activity]
        for i, activity in enumerate(ACTIVITIES)
    ]

    weights = [
        PRIORITY_WEIGHTS[activity]
        for activity in ACTIVITIES
    ]

    # 4. Check whether the budget can satisfy all minimum allocations
    minimum_required = sum(minimum_allocation)

    if available_budget < minimum_required - 1e-9:
        return {
            "success": False,
            "message": (
                "Infeasible budget: available water is lower "
                "than the minimum required allocation."
            ),
            "total_predicted_demand_liters": round(sum(demand), 2),
            "available_budget_liters": round(float(available_budget), 2),
            "minimum_required_liters": round(minimum_required, 2)
        }

    # 5. Define the LP objective.
    # linprog minimizes, so negative weights maximize priority.
    objective = [-weight for weight in weights]

    # 6. Total allocation must not exceed the available budget
    constraints = [[1, 1, 1, 1]]
    constraint_limits = [float(available_budget)]

    # 7. Each activity must stay between its minimum and predicted demand
    bounds = [
        (minimum_allocation[i], demand[i])
        for i in range(len(ACTIVITIES))
    ]

    # 8. Solve the Linear Programming problem
    result = linprog(
        c=objective,
        A_ub=constraints,
        b_ub=constraint_limits,
        bounds=bounds,
        method="highs"
    )

    if not result.success:
        return {
            "success": False,
            "message": f"Optimization failed: {result.message}"
        }

    # 9. Extract optimized allocations
    allocations = {
        activity: max(0.0, float(result.x[i]))
        for i, activity in enumerate(ACTIVITIES)
    }

    total_demand = sum(demand)
    total_allocated = sum(allocations.values())
    potential_savings = total_demand - total_allocated

    savings_percentage = (
        potential_savings / total_demand * 100
        if total_demand > 0 else 0
    )

    # 10. Return the optimization results
    return {
        "success": True,
        "message": "Water allocation optimized successfully.",
        "total_predicted_demand_liters": round(total_demand, 2),
        "available_budget_liters": round(
            float(available_budget), 2
        ),
        "total_allocated_liters": round(total_allocated, 2),
        "potential_savings_liters": round(
            potential_savings, 2
        ),
        "potential_savings_percentage": round(
            savings_percentage, 2
        ),
        "activity_allocations": {
            activity: {
                "predicted_liters": round(demand[i], 2),
                "minimum_liters": round(minimum_allocation[i], 2),
                "optimized_liters": round(allocations[activity], 2),
                "water_reduced_liters": round(
                    demand[i] - allocations[activity], 2
                )
            }
            for i, activity in enumerate(ACTIVITIES)
        }
    }


# Independent test
if __name__ == "__main__":

    sample_demand = {
        "bathroom": 241.65,
        "kitchen": 62.81,
        "laundry": 58.99,
        "gardening": 36.39
    }

    daily_budget = 350

    result = optimize_water_allocation(
        sample_demand,
        daily_budget
    )

    print("\n========== WATER OPTIMIZATION RESULT ==========")

    for key, value in result.items():
        print(f"{key}: {value}")
