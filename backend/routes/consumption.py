
from flask import Blueprint, request, jsonify
from database.db import get_db_connection

from datetime import datetime
import math

consumption_bp = Blueprint("consumption", __name__)


# API 1: Record daily water consumption
@consumption_bp.route("/api/consumption", methods=["POST"])
def add_consumption():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must contain valid JSON."
        }), 400

    household_id = data.get("household_id")
    record_date = data.get("record_date")

    # Validate household ID
    if (
        isinstance(household_id, bool)
        or not isinstance(household_id, int)
        or household_id <= 0
    ):
        return jsonify({
            "error": "A valid household_id is required."
        }), 400

    # Validate date
    if not isinstance(record_date, str):
        return jsonify({
            "error": "record_date is required in YYYY-MM-DD format."
        }), 400

    try:
        datetime.strptime(record_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({
            "error": "Invalid date. Use YYYY-MM-DD format."
        }), 400

    # Activity categories
    activities = [
        "bathroom_liters",
        "kitchen_liters",
        "laundry_liters",
        "gardening_liters"
    ]

    consumption = {}

    # Validate each activity's water consumption
    for activity in activities:

        value = data.get(activity, 0)

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            return jsonify({
                "error": f"{activity} must be a valid non-negative number."
            }), 400

        consumption[activity] = float(value)

    # Calculate total on the backend
    total_liters = sum(consumption.values())

    connection = get_db_connection()

    try:
        # Check whether household exists
        household = connection.execute(
            "SELECT household_id FROM households WHERE household_id = ?",
            (household_id,)
        ).fetchone()

        if household is None:
            return jsonify({
                "error": "Household not found."
            }), 404

        connection.execute(
            """
            INSERT INTO consumption_records (
                household_id,
                record_date,
                bathroom_liters,
                kitchen_liters,
                laundry_liters,
                gardening_liters,
                total_liters
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                household_id,
                record_date,
                consumption["bathroom_liters"],
                consumption["kitchen_liters"],
                consumption["laundry_liters"],
                consumption["gardening_liters"],
                total_liters
            )
        )

        connection.commit()

        return jsonify({
            "message": "Daily consumption recorded successfully!",
            "household_id": household_id,
            "record_date": record_date,
            "activity_consumption": consumption,
            "total_liters": total_liters
        }), 201

    except Exception as error:
        from sqlite3 import IntegrityError

        if isinstance(error, IntegrityError):
            return jsonify({
                "error": "A consumption record already exists for this household and date."
            }), 409

        raise

    finally:
        connection.close()


# API 2: Retrieve consumption history
@consumption_bp.route(
    "/api/consumption/<int:household_id>",
    methods=["GET"]
)
def get_consumption(household_id):

    connection = get_db_connection()

    try:
        household = connection.execute(
            "SELECT household_id FROM households WHERE household_id = ?",
            (household_id,)
        ).fetchone()

        if household is None:
            return jsonify({
                "error": "Household not found."
            }), 404

        records = connection.execute(
            """
            SELECT
                record_id,
                household_id,
                record_date,
                bathroom_liters,
                kitchen_liters,
                laundry_liters,
                gardening_liters,
                total_liters
            FROM consumption_records
            WHERE household_id = ?
            ORDER BY record_date DESC
            """,
            (household_id,)
        ).fetchall()

        result = [dict(row) for row in records]

        return jsonify({
            "household_id": household_id,
            "total_records": len(result),
            "records": result
        }), 200

    finally:
        connection.close()
