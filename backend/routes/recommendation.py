
from flask import Blueprint, request, jsonify
from routes.prediction import model
from optimization.optimizer import optimize_water_allocation
import pandas as pd

from recommendations.conservation import (
    generate_conservation_recommendations
)

from validation.input_validator import validate_household_input


recommendation_bp = Blueprint("recommendation", __name__)


@recommendation_bp.route("/api/recommend", methods=["POST"])
def generate_recommendation():

    data = request.get_json(silent=True)

    validated_data, error = validate_household_input(
        data,
        require_budget=True
    )

    if error:
        return jsonify({"error": error}), 400

    household_size = validated_data["Household_Size"]

    # Prepare KNN input
    input_data = pd.DataFrame([{
        "Household_Size": household_size,
        "Bathing_Events": validated_data["Bathing_Events"],
        "Kitchen_Sessions": validated_data["Kitchen_Sessions"],
        "Laundry_Loads": validated_data["Laundry_Loads"],
        "Gardening_Duration_Minutes":
            validated_data["Gardening_Duration_Minutes"]
    }])

    # Generate KNN predictions
    predictions = model.predict(input_data)[0]

    predicted_demand = {
        "bathroom": max(0, float(predictions[0])),
        "kitchen": max(0, float(predictions[1])),
        "laundry": max(0, float(predictions[2])),
        "gardening": max(0, float(predictions[3]))
    }

    # Enforce zero-activity constraints
    if validated_data["Laundry_Loads"] == 0:
        predicted_demand["laundry"] = 0

    if validated_data["Gardening_Duration_Minutes"] == 0:
        predicted_demand["gardening"] = 0

    # Run water optimization
    optimization_result = optimize_water_allocation(
        predicted_demand,
        validated_data["available_budget_liters"]
    )

    # Generate conservation recommendations
    conservation_result = generate_conservation_recommendations(
        optimization_result
    )

    return jsonify({
        "household_size": household_size,

        "predicted_consumption": {
            key: round(value, 2)
            for key, value in predicted_demand.items()
        },

        "optimization": optimization_result,

        "conservation_recommendations": conservation_result

    }), 200 if optimization_result["success"] else 422
