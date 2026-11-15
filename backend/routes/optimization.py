
from flask import Blueprint, request, jsonify
from optimization.optimizer import optimize_water_allocation

optimization_bp = Blueprint("optimization", __name__)


@optimization_bp.route("/api/optimize", methods=["POST"])
def optimize_consumption():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON input is required."
        }), 400

    predicted_demand = data.get("predicted_consumption")
    available_budget = data.get("available_budget_liters")

    if not isinstance(predicted_demand, dict):
        return jsonify({
            "error": "predicted_consumption must be a JSON object."
        }), 400

    if available_budget is None:
        return jsonify({
            "error": "available_budget_liters is required."
        }), 400

    try:
        result = optimize_water_allocation(
            predicted_demand,
            available_budget
        )

        if not result["success"]:
            return jsonify(result), 422

        return jsonify(result), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400
