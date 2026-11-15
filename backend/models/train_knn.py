
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import (
    GroupShuffleSplit,
    GroupKFold,
    GridSearchCV
)

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# --------------------------------------------------
# 1. PATH CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "synthetic"
    / "simulated_household_water_consumption.csv"
)

MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOAD DATASET
# --------------------------------------------------

df = pd.read_csv(DATA_FILE)

print("\n========== DATASET LOADED ==========")
print("Dataset shape:", df.shape)


# --------------------------------------------------
# 3. DEFINE INPUT FEATURES AND TARGETS
# --------------------------------------------------

input_features = [
    "Household_Size",
    "Bathing_Events",
    "Kitchen_Sessions",
    "Laundry_Loads",
    "Gardening_Duration_Minutes"
]

target_features = [
    "Bathroom_Liters",
    "Kitchen_Liters",
    "Laundry_Liters",
    "Gardening_Liters"
]

X = df[input_features]
y = df[target_features]

# Household_ID is used only to separate households
# during training and testing.
groups = df["Household_ID"]


# --------------------------------------------------
# 4. SPLIT DATA BY HOUSEHOLD
# --------------------------------------------------

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_indices, test_indices = next(
    splitter.split(X, y, groups=groups)
)

X_train = X.iloc[train_indices]
X_test = X.iloc[test_indices]

y_train = y.iloc[train_indices]
y_test = y.iloc[test_indices]

groups_train = groups.iloc[train_indices]
groups_test = groups.iloc[test_indices]

print("\n========== TRAIN-TEST SPLIT ==========")

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

print("Training households:", groups_train.nunique())
print("Testing households:", groups_test.nunique())

print(
    "Household overlap:",
    len(set(groups_train) & set(groups_test))
)


# --------------------------------------------------
# 5. BUILD KNN PIPELINE
# --------------------------------------------------

pipeline = Pipeline([
    ("scaler", StandardScaler()),

    ("knn", KNeighborsRegressor())
])


# --------------------------------------------------
# 6. HYPERPARAMETER TUNING
# --------------------------------------------------

parameter_grid = {
    "knn__n_neighbors": [3, 5, 7, 9, 11, 15, 21, 31],
    "knn__weights": ["uniform", "distance"],
    "knn__p": [1, 2]
}

group_cv = GroupKFold(n_splits=5)

grid_search = GridSearchCV(
    estimator=pipeline,
    param_grid=parameter_grid,
    scoring="neg_mean_absolute_error",
    cv=group_cv,
    n_jobs=-1,
    verbose=1
)

print("\n========== HYPERPARAMETER TUNING ==========")

grid_search.fit(
    X_train,
    y_train,
    groups=groups_train
)

best_model = grid_search.best_estimator_

print("\nBest parameters:")
print(grid_search.best_params_)

print(
    "\nBest cross-validation MAE:",
    round(-grid_search.best_score_, 2),
    "liters"
)


# --------------------------------------------------
# 7. PREDICT ON UNSEEN HOUSEHOLDS
# --------------------------------------------------

predictions = best_model.predict(X_test)

prediction_df = pd.DataFrame(
    predictions,
    columns=[
        f"Predicted_{column}"
        for column in target_features
    ],
    index=X_test.index
)

actual_df = y_test.add_prefix("Actual_")

results = pd.concat(
    [
        df.loc[X_test.index, ["Date", "Household_ID"]],
        actual_df,
        prediction_df
    ],
    axis=1
)

results["Actual_Total_Liters"] = y_test.sum(axis=1)

results["Predicted_Total_Liters"] = (
    prediction_df.sum(axis=1)
)


# --------------------------------------------------
# 8. EVALUATE MODEL
# --------------------------------------------------

print("\n========== MODEL EVALUATION ==========")

metrics = []

for index, target in enumerate(target_features):

    actual = y_test.iloc[:, index]
    predicted = predictions[:, index]

    mae = mean_absolute_error(actual, predicted)

    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    r2 = r2_score(actual, predicted)

    metrics.append({
        "Target": target,
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "R2": round(r2, 4)
    })

    print(f"\n{target}")
    print("MAE:", round(mae, 2), "liters")
    print("RMSE:", round(rmse, 2), "liters")
    print("R2:", round(r2, 4))


# Evaluate total consumption separately

total_mae = mean_absolute_error(
    results["Actual_Total_Liters"],
    results["Predicted_Total_Liters"]
)

total_rmse = np.sqrt(
    mean_squared_error(
        results["Actual_Total_Liters"],
        results["Predicted_Total_Liters"]
    )
)

total_r2 = r2_score(
    results["Actual_Total_Liters"],
    results["Predicted_Total_Liters"]
)

print("\nTOTAL CONSUMPTION")
print("MAE:", round(total_mae, 2), "liters")
print("RMSE:", round(total_rmse, 2), "liters")
print("R2:", round(total_r2, 4))


# --------------------------------------------------
# 9. SAVE MODEL AND RESULTS
# --------------------------------------------------

MODEL_FILE = MODEL_DIR / "knn_water_consumption.joblib"

METRICS_FILE = OUTPUT_DIR / "knn_evaluation_metrics.csv"

PREDICTIONS_FILE = OUTPUT_DIR / "knn_test_predictions.csv"

joblib.dump(best_model, MODEL_FILE)

pd.DataFrame(metrics).to_csv(
    METRICS_FILE,
    index=False
)

results.to_csv(
    PREDICTIONS_FILE,
    index=False
)


# --------------------------------------------------
# 10. FINAL SUMMARY
# --------------------------------------------------

print("\n========== MODEL TRAINING COMPLETED ==========")

print("Best KNN model saved at:")
print(MODEL_FILE)

print("\nEvaluation metrics saved at:")
print(METRICS_FILE)

print("\nTest predictions saved at:")
print(PREDICTIONS_FILE)

print("\nTraining data source: SIMULATED")
print("Testing data source: SIMULATED")
