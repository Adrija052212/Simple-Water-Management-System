
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# --------------------------------------------------
# 1. LOAD DATASET
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = (
    BASE_DIR
    / "synthetic"
    / "simulated_household_water_consumption.csv"
)

OUTPUT_DIR = BASE_DIR / "processed" / "eda"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE)

df["Date"] = pd.to_datetime(df["Date"])

sns.set_theme(style="whitegrid")


# --------------------------------------------------
# 2. BASIC DATASET INFORMATION
# --------------------------------------------------

print("\n========== DATASET OVERVIEW ==========")

print("Shape:", df.shape)

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())

print("\nNumber of households:", df["Household_ID"].nunique())

print("\nRecords per household:")
print(df.groupby("Household_ID").size().describe())


# --------------------------------------------------
# 3. CONSUMPTION STATISTICS
# --------------------------------------------------

activity_columns = [
    "Bathroom_Liters",
    "Kitchen_Liters",
    "Laundry_Liters",
    "Gardening_Liters"
]

print("\n========== CONSUMPTION STATISTICS ==========")

print(
    df[activity_columns + ["Total_Liters"]]
    .describe()
    .round(2)
)

print("\nAverage consumption by activity:")
print(df[activity_columns].mean().round(2))


# --------------------------------------------------
# 4. HOUSEHOLD SIZE ANALYSIS
# --------------------------------------------------

print("\n========== HOUSEHOLD SIZE ANALYSIS ==========")

household_analysis = (
    df.groupby("Household_Size")
    [activity_columns + ["Total_Liters"]]
    .mean()
    .round(2)
)

print(household_analysis)


# --------------------------------------------------
# 5. INPUT-TARGET RELATIONSHIPS
# --------------------------------------------------

print("\n========== INPUT-TARGET RELATIONSHIPS ==========")

input_columns = [
    "Household_Size",
    "Bathing_Events",
    "Kitchen_Sessions",
    "Laundry_Loads",
    "Gardening_Duration_Minutes"
]

relationships = [
    ("Bathing_Events", "Bathroom_Liters"),
    ("Kitchen_Sessions", "Kitchen_Liters"),
    ("Laundry_Loads", "Laundry_Liters"),
    ("Gardening_Duration_Minutes", "Gardening_Liters")
]

for input_feature, target in relationships:

    correlation = df[input_feature].corr(df[target])

    print(
        f"{input_feature} vs {target}: "
        f"{correlation:.3f}"
    )


# --------------------------------------------------
# 6. CORRELATION ANALYSIS
# --------------------------------------------------

numeric_columns = input_columns + activity_columns + ["Total_Liters"]

correlation_matrix = df[numeric_columns].corr()

print("\n========== CORRELATION MATRIX ==========")

print(correlation_matrix.round(2))


# --------------------------------------------------
# 7. TOTAL CONSUMPTION VALIDATION
# --------------------------------------------------

calculated_total = df[activity_columns].sum(axis=1)

total_mismatches = (
    (calculated_total - df["Total_Liters"]).abs() > 0.011
).sum()

print("\n========== DATA CONSISTENCY ==========")

print("Total consumption mismatches:", total_mismatches)

print(
    "Zero-load laundry records:",
    ((df["Laundry_Loads"] == 0) &
     (df["Laundry_Liters"] != 0)).sum()
)

print(
    "Zero-duration gardening records:",
    ((df["Gardening_Duration_Minutes"] == 0) &
     (df["Gardening_Liters"] != 0)).sum()
)


# --------------------------------------------------
# 8. OUTLIER DETECTION USING IQR
# --------------------------------------------------

print("\n========== OUTLIER DETECTION ==========")

for column in activity_columns + ["Total_Liters"]:

    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)

    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers = df[
        (df[column] < lower_bound) |
        (df[column] > upper_bound)
    ]

    print(f"{column}: {len(outliers)} potential outliers")


# --------------------------------------------------
# 9. VISUALIZATION 1: CONSUMPTION DISTRIBUTIONS
# --------------------------------------------------

plt.figure(figsize=(12, 7))

for column in activity_columns:

    sns.histplot(
        data=df,
        x=column,
        kde=True,
        label=column,
        alpha=0.35
    )

plt.title("Distribution of Household Water Consumption")
plt.xlabel("Water Consumption (Liters)")
plt.ylabel("Frequency")
plt.legend()

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "consumption_distributions.png")
plt.close()


# --------------------------------------------------
# 10. VISUALIZATION 2: CONSUMPTION BY HOUSEHOLD SIZE
# --------------------------------------------------

household_plot = (
    df.groupby("Household_Size")
    [activity_columns + ["Total_Liters"]]
    .mean()
    .reset_index()
)

plt.figure(figsize=(11, 6))

sns.lineplot(
    data=household_plot,
    x="Household_Size",
    y="Total_Liters",
    marker="o"
)

plt.title("Average Total Consumption by Household Size")
plt.xlabel("Number of Household Members")
plt.ylabel("Average Consumption (Liters)")
plt.tight_layout()

plt.savefig(OUTPUT_DIR / "consumption_by_household_size.png")
plt.close()


# --------------------------------------------------
# 11. VISUALIZATION 3: INPUT-TARGET RELATIONSHIPS
# --------------------------------------------------

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

for ax, (input_feature, target) in zip(
    axes.flatten(),
    relationships
):

    sns.scatterplot(
        data=df,
        x=input_feature,
        y=target,
        alpha=0.45,
        ax=ax
    )

    ax.set_title(f"{input_feature} vs {target}")

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "input_target_relationships.png")
plt.close()


# --------------------------------------------------
# 12. VISUALIZATION 4: CORRELATION HEATMAP
# --------------------------------------------------

plt.figure(figsize=(13, 10))

sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=0.5
)

plt.title("Feature Correlation Heatmap")
plt.tight_layout()

plt.savefig(OUTPUT_DIR / "correlation_heatmap.png")
plt.close()


# --------------------------------------------------
# 13. VISUALIZATION 5: ACTIVITY-WISE BOXPLOTS
# --------------------------------------------------

plt.figure(figsize=(11, 6))

sns.boxplot(
    data=df[activity_columns]
)

plt.title("Activity-wise Water Consumption")
plt.ylabel("Water Consumption (Liters)")
plt.xticks(rotation=15)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "activity_boxplots.png")
plt.close()


# --------------------------------------------------
# 14. FINAL MESSAGE
# --------------------------------------------------

print("\n========== EDA COMPLETED ==========")

print("All analysis plots saved inside:")
print(OUTPUT_DIR)
