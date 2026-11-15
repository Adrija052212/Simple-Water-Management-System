
from pathlib import Path

import numpy as np
import pandas as pd


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

RANDOM_SEED = 42
NUMBER_OF_HOUSEHOLDS = 100
DAYS_PER_HOUSEHOLD = 20
START_DATE = "2026-01-01"

rng = np.random.default_rng(RANDOM_SEED)


# --------------------------------------------------
# 2. OUTPUT DIRECTORY
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "synthetic"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "simulated_household_water_consumption.csv"


# --------------------------------------------------
# 3. GENERATE HOUSEHOLD INFORMATION
# --------------------------------------------------

households = []

for household_id in range(1, NUMBER_OF_HOUSEHOLDS + 1):

    household_size = int(rng.integers(1, 7))

    households.append({
        "Household_ID": household_id,
        "Household_Size": household_size
    })


# --------------------------------------------------
# 4. GENERATE DAILY CONSUMPTION RECORDS
# --------------------------------------------------

records = []

start_date = pd.Timestamp(START_DATE)

for household in households:

    household_id = household["Household_ID"]
    household_size = household["Household_Size"]

    for day in range(DAYS_PER_HOUSEHOLD):

        record_date = start_date + pd.Timedelta(days=day)

        # Number of bathing events
        bathing_events = int(
            rng.binomial(household_size, 0.90)
        )

        # Number of kitchen cooking sessions
        kitchen_sessions = int(
            rng.integers(2, 5)
        )

        # Laundry loads depend partly on household size
        laundry_loads = min(
            int(rng.poisson(household_size / 4)),
            3
        )

        # Gardening duration (minutes)
        if rng.random() < 0.55:
            gardening_duration = 0
        else:
            gardening_duration = int(
                rng.integers(10, 61)
            )

        # --------------------------------------------------
        # 5. SIMULATE ACTIVITY-WISE WATER CONSUMPTION
        # --------------------------------------------------

        # Bathroom:
        # Water for bathing + other bathroom activities
        bathroom_liters = (
            bathing_events * rng.uniform(40, 55)
            + household_size * rng.uniform(8, 13)
            + rng.normal(0, 5)
        )

        # Kitchen:
        # Water for cooking and dishwashing
        kitchen_liters = (
            kitchen_sessions * rng.uniform(10, 16)
            + household_size * rng.uniform(5, 8)
            + rng.normal(0, 3)
        )

        # Laundry:
        # Each laundry load consumes approximately 50-75 L
        if laundry_loads == 0:
            laundry_liters = 0
        else:
            laundry_liters = (
                laundry_loads * rng.uniform(50, 75)
                + rng.normal(0, 3)
            )

        # Gardening:
        # Water consumption depends on irrigation duration
        if gardening_duration == 0:
            gardening_liters = 0
        else:
            gardening_liters = (
                gardening_duration * rng.uniform(2.0, 3.0)
                + rng.normal(0, 3)
            )

        # Prevent negative consumption values
        bathroom_liters = max(0, bathroom_liters)
        kitchen_liters = max(0, kitchen_liters)
        laundry_liters = max(0, laundry_liters)
        gardening_liters = max(0, gardening_liters)

        # Round activity-wise consumption
        bathroom_liters = round(bathroom_liters, 2)
        kitchen_liters = round(kitchen_liters, 2)
        laundry_liters = round(laundry_liters, 2)
        gardening_liters = round(gardening_liters, 2)

        # Calculate total consumption
        total_liters = round(
            bathroom_liters
            + kitchen_liters
            + laundry_liters
            + gardening_liters,
            2
        )

        # --------------------------------------------------
        # 6. STORE THE RECORD
        # --------------------------------------------------

        records.append({
            "Date": record_date.strftime("%Y-%m-%d"),
            "Household_ID": household_id,
            "Household_Size": household_size,

            "Bathing_Events": bathing_events,
            "Kitchen_Sessions": kitchen_sessions,
            "Laundry_Loads": laundry_loads,
            "Gardening_Duration_Minutes": gardening_duration,

            "Bathroom_Liters": bathroom_liters,
            "Kitchen_Liters": kitchen_liters,
            "Laundry_Liters": laundry_liters,
            "Gardening_Liters": gardening_liters,

            "Total_Liters": total_liters,

            "Data_Source": "SIMULATED"
        })


# --------------------------------------------------
# 7. CREATE AND SAVE DATASET
# --------------------------------------------------

df = pd.DataFrame(records)

df.to_csv(OUTPUT_FILE, index=False)


# --------------------------------------------------
# 8. DISPLAY DATASET SUMMARY
# --------------------------------------------------

print("\nSIMULATED DATASET GENERATED SUCCESSFULLY!")

print("\nDataset shape:", df.shape)

print("\nFirst 10 records:")
print(df.head(10).to_string(index=False))

print("\nMissing values:")
print(df.isnull().sum())

print("\nConsumption statistics:")
print(
    df[
        [
            "Bathroom_Liters",
            "Kitchen_Liters",
            "Laundry_Liters",
            "Gardening_Liters",
            "Total_Liters"
        ]
    ].describe().round(2)
)

print("\nHousehold count:", df["Household_ID"].nunique())

print("Records per household:")
print(df.groupby("Household_ID").size().value_counts())

print("\nData source:", df["Data_Source"].unique())

print("\nSaved at:", OUTPUT_FILE)
