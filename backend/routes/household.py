
from flask import Blueprint, request, jsonify
from database.db import get_db_connection

# Create a Blueprint for household-related APIs
household_bp = Blueprint("household", __name__)


# API 1: Register a new household
@household_bp.route("/api/households", methods=["POST"])
def create_household():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must contain valid JSON."
        }), 400

    household_name = data.get("household_name", "")
    household_size = data.get("household_size")

    # Validate household name
    if not isinstance(household_name, str):
        return jsonify({
            "error": "Household name must be text."
        }), 400

    household_name = household_name.strip()

    # Validate household size
    if (
        isinstance(household_size, bool)
        or not isinstance(household_size, int)
        or household_size <= 0
    ):
        return jsonify({
            "error": "Household size must be a positive integer."
        }), 400

    connection = get_db_connection()

    try:
        # Check whether a household is already registered
        existing_household = connection.execute(
            "SELECT household_id FROM households LIMIT 1"
        ).fetchone()

        if existing_household:
            return jsonify({
                "error": "A household is already registered. Only one household is allowed."
            }), 409

        # Register the household if none exists
        cursor = connection.execute(
            """
            INSERT INTO households (household_name, household_size)
            VALUES (?, ?)
            """,
            (household_name or None, household_size)
        )

        connection.commit()

        new_household_id = cursor.lastrowid

        return jsonify({
            "message": "Household registered successfully!",
            "household_id": new_household_id,
            "household_name": household_name,
            "household_size": household_size
        }), 201

    finally:
        connection.close()


# API 2: Retrieve all registered households
@household_bp.route("/api/households", methods=["GET"])
def get_households():

    connection = get_db_connection()

    try:
        households = connection.execute(
            """
            SELECT household_id, household_name,
                   household_size, created_at
            FROM households
            ORDER BY household_id
            """
        ).fetchall()

        result = [dict(row) for row in households]

        return jsonify({
            "total_households": len(result),
            "households": result
        }), 200

    finally:
        connection.close()


# TEMPORARY: Remove duplicate test household
@household_bp.route("/api/households/cleanup", methods=["POST"])
def cleanup_duplicate_household():

    connection = get_db_connection()

    try:
        # Confirm that household ID 1 exists
        primary = connection.execute(
            "SELECT household_id FROM households WHERE household_id = 1"
        ).fetchone()

        if not primary:
            return jsonify({
                "error": "Primary household ID 1 was not found."
            }), 404

        # Check whether household ID 2 has consumption records
        records = connection.execute(
            "SELECT COUNT(*) AS total FROM consumption_records WHERE household_id = 2"
        ).fetchone()["total"]

        if records > 0:
            return jsonify({
                "error": "Household ID 2 has consumption records. Deletion cancelled."
            }), 409

        # Delete duplicate household ID 2
        connection.execute(
            "DELETE FROM households WHERE household_id = 2"
        )

        connection.commit()

        return jsonify({
            "message": "Duplicate household removed successfully."
        }), 200

    finally:
        connection.close()