
from pathlib import Path

import joblib
import pandas as pd


# --------------------------------------------------
# 1. LOAD TRAINED MODEL
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_FILE = BASE_DIR / "models" / "knn_water_consumption.joblib"

model = joblib.load(MODEL_FILE)


# --------------------------------------------------
# 2. CREATE SAMPLE HOUSEHOLD INPUTS
# --------------------------------------------------

samples = pd.DataFrame([
    {
        "Household_Size": 1,
        "Bathing_Events": 1,
        "Kitchen_Sessions": 3,
        "Laundry_Loads": 0,
        "Gardening_Duration_Minutes": 0
    },
    {
        "Household_Size": 4,
        "Bathing_Events": 4,
        "Kitchen_Sessions": 3,
        "Laundry_Loads": 1,
        "Gardening_Duration_Minutes": 20
    },
    {
        "Household_Size": 6,
        "Bathing_Events": 6,
        "Kitchen_Sessions": 4,
        "Laundry_Loads": 3,
        "Gardening_Duration_Minutes": 45
    }
])


# --------------------------------------------------
# 3. GENERATE PREDICTIONS
# --------------------------------------------------

predictions = model.predict(samples)

target_columns = [
    "Bathroom_Liters",
    "Kitchen_Liters",
    "Laundry_Liters",
    "Gardening_Liters"
]

results = pd.DataFrame(
    predictions,
    columns=target_columns
)


# --------------------------------------------------
# 4. APPLY LOGICAL CONSTRAINTS
# --------------------------------------------------

results.loc[
    samples["Laundry_Loads"].to_numpy() == 0,
    "Laundry_Liters"
] = 0

results.loc[
    samples["Gardening_Duration_Minutes"].to_numpy() == 0,
    "Gardening_Liters"
] = 0

# Consumption cannot be negative.
results[target_columns] = results[target_columns].clip(lower=0)

results["Total_Liters"] = results[target_columns].sum(axis=1)


# --------------------------------------------------
# 5. DISPLAY RESULTS
# --------------------------------------------------

print("\n========== KNN SAMPLE PREDICTIONS ==========")

output = pd.concat(
    [
        samples.reset_index(drop=True),
        results.round(2)
    ],
    axis=1
)

print(output.to_string(index=False))

print("\nPrediction validation:")

print(
    "Negative predictions:",
    (results[target_columns] < 0).sum().sum()
)

print(
    "Zero-load laundry violations:",
    (
        (samples["Laundry_Loads"] == 0)
        & (results["Laundry_Liters"] != 0)
    ).sum()
)

print(
    "Zero-duration gardening violations:",
    (
        (samples["Gardening_Duration_Minutes"] == 0)
        & (results["Gardening_Liters"] != 0)
    ).sum()
)

print(
    "Total calculation mismatches:",
    (
        (
            results["Total_Liters"]
            - results[target_columns].sum(axis=1)
        ).abs() > 0.001
    ).sum()
)
