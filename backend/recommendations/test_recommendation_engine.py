
from recommendations.conservation import (
    generate_conservation_recommendations
)

sample_optimization = {
    "success": True,
    "activity_allocations": {
        "bathroom": {
            "predicted_liters": 241.65,
            "optimized_liters": 241.65,
            "water_reduced_liters": 0
        },
        "kitchen": {
            "predicted_liters": 62.81,
            "optimized_liters": 62.81,
            "water_reduced_liters": 0
        },
        "laundry": {
            "predicted_liters": 58.99,
            "optimized_liters": 45.54,
            "water_reduced_liters": 13.45
        },
        "gardening": {
            "predicted_liters": 36.39,
            "optimized_liters": 0,
            "water_reduced_liters": 36.39
        }
    }
}

result = generate_conservation_recommendations(
    sample_optimization
)

print("\n========== CONSERVATION RECOMMENDATIONS ==========")

print("Status:", result["status"])
print("Message:", result["message"])

for recommendation in result["recommendations"]:
    print("\nActivity:", recommendation["activity"])
    print("Title:", recommendation["title"])
    print("Priority:", recommendation["priority"])
    print(
        "Target reduction:",
        recommendation["target_reduction_liters"],
        "litres"
    )
    print("Actions:")

    for action in recommendation["actions"]:
        print("-", action)

print("\nDisclaimer:", result["disclaimer"])
