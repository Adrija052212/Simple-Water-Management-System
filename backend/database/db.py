
import sqlite3
from pathlib import Path

# Locate the backend directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database file location
DATABASE_PATH = BASE_DIR / "database" / "water_consumption.db"

# SQL schema location
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def get_db_connection():
    """Create and return a database connection."""

    connection = sqlite3.connect(DATABASE_PATH)

    # Return rows in dictionary-like format
    connection.row_factory = sqlite3.Row

    # Enable foreign key validation
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """Create database tables if they do not exist."""

    connection = get_db_connection()

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
            schema = file.read()

        connection.executescript(schema)
        connection.commit()

        print("Database initialized successfully!")

    finally:
        connection.close()
