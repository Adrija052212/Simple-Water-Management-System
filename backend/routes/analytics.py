
from flask import Blueprint, jsonify
from database.db import get_db_connection

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route(
    "/api/analytics/<int:household_id>",
    methods=["GET"]
)
def get_analytics(household_id):

    connection = get_db_connection()

    try:
        # Retrieve household information
        household = connection.execute(
            """
            SELECT household_id, household_name, household_size
            FROM households
            WHERE household_id = ?
            """,
            (household_id,)
        ).fetchone()

        if household is None:
            return jsonify({
                "error": "Household not found."
            }), 404

        # Calculate consumption statistics
        stats = connection.execute(
            """
            SELECT
                COUNT(*) AS total_records,
                COALESCE(SUM(total_liters), 0) AS total_consumption,
                COALESCE(AVG(total_liters), 0) AS average_daily_consumption,
                COALESCE(SUM(bathroom_liters), 0) AS bathroom_total,
                COALESCE(SUM(kitchen_liters), 0) AS kitchen_total,
                COALESCE(SUM(laundry_liters), 0) AS laundry_total,
                COALESCE(SUM(gardening_liters), 0) AS gardening_total
            FROM consumption_records
            WHERE household_id = ?
            """,
            (household_id,)
        ).fetchone()

        total = stats["total_consumption"]
        household_size = household["household_size"]

        activities = {
            "bathroom": stats["bathroom_total"],
            "kitchen": stats["kitchen_total"],
            "laundry": stats["laundry_total"],
            "gardening": stats["gardening_total"]
        }

        # Calculate activity-wise percentage contribution
        breakdown = {}

        for activity, value in activities.items():
            percentage = (value / total * 100) if total > 0 else 0

            breakdown[activity] = {
                "total_liters": round(value, 2),
                "percentage": round(percentage, 2)
            }

        # Identify the highest-consuming activity
        highest_activity = (
            max(activities, key=activities.get)
            if total > 0 else None
        )

        return jsonify({
            "household": {
                "household_id": household["household_id"],
                "household_name": household["household_name"],
                "household_size": household_size
            },
            "summary": {
                "total_records": stats["total_records"],
                "total_consumption_liters": round(total, 2),
                "average_per_record_liters": round(
                    stats["average_daily_consumption"], 2
                ),
                "average_per_person_per_record_liters": round(
                    stats["average_daily_consumption"] / household_size, 2
                )
            },
            "activity_breakdown": breakdown,
            "highest_consuming_activity": highest_activity
        }), 200

    finally:
        connection.close()
