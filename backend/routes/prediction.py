
from flask import Blueprint, request, jsonify
from pathlib import Path
import joblib
import pandas as pd

from validation.input_validator import validate_household_input

prediction_bp = Blueprint("prediction", __name__)

# Locate the saved KNN model
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_FILE = BASE_DIR / "models" / "knn_water_consumption.joblib"

# Load the model once when Flask starts
model = joblib.load(MODEL_FILE)


@prediction_bp.route("/api/predict", methods=["POST"])
def predict_consumption():

    data = request.get_json(silent=True)

    # Use the shared input validator
    validated_data, error = validate_household_input(data)

    if error:
        return jsonify({"error": error}), 400

    household_size = validated_data["Household_Size"]

    # Prepare input in the exact feature order used during training
    input_data = pd.DataFrame([{
        "Household_Size": household_size,
        "Bathing_Events": validated_data["Bathing_Events"],
        "Kitchen_Sessions": validated_data["Kitchen_Sessions"],
        "Laundry_Loads": validated_data["Laundry_Loads"],
        "Gardening_Duration_Minutes":
            validated_data["Gardening_Duration_Minutes"]
    }])

    # Generate predictions
    predictions = model.predict(input_data)[0]

    activity_names = [
        "Bathroom_Liters",
        "Kitchen_Liters",
        "Laundry_Liters",
        "Gardening_Liters"
    ]

    results = dict(zip(activity_names, predictions))

    # Apply physical constraints
    if validated_data["Laundry_Loads"] == 0:
        results["Laundry_Liters"] = 0

    if validated_data["Gardening_Duration_Minutes"] == 0:
        results["Gardening_Liters"] = 0

    results = {
        key: max(0, float(value))
        for key, value in results.items()
    }

    total_liters = sum(results.values())

    return jsonify({
        "message": "Water consumption predicted successfully.",
        "prediction_type": "KNN regression on simulated training data",
        "household_size": household_size,
        "predicted_consumption": {
            "bathroom_liters": round(results["Bathroom_Liters"], 2),
            "kitchen_liters": round(results["Kitchen_Liters"], 2),
            "laundry_liters": round(results["Laundry_Liters"], 2),
            "gardening_liters": round(results["Gardening_Liters"], 2),
            "total_liters": round(total_liters, 2)
        }
    }), 200
