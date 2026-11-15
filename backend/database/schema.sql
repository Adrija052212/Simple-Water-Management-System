
-- Household information
CREATE TABLE IF NOT EXISTS households (
    household_id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_name TEXT,
    household_size INTEGER NOT NULL CHECK (household_size > 0),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Daily household water consumption
CREATE TABLE IF NOT EXISTS consumption_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,

    household_id INTEGER NOT NULL,

    record_date TEXT NOT NULL,

    bathroom_liters REAL NOT NULL DEFAULT 0
        CHECK (bathroom_liters >= 0),

    kitchen_liters REAL NOT NULL DEFAULT 0
        CHECK (kitchen_liters >= 0),

    laundry_liters REAL NOT NULL DEFAULT 0
        CHECK (laundry_liters >= 0),

    gardening_liters REAL NOT NULL DEFAULT 0
        CHECK (gardening_liters >= 0),

    total_liters REAL NOT NULL
        CHECK (total_liters >= 0),

    FOREIGN KEY (household_id)
        REFERENCES households(household_id),

    UNIQUE (household_id, record_date),

    CHECK (
        ABS(total_liters - (
            bathroom_liters +
            kitchen_liters +
            laundry_liters +
            gardening_liters
        )) < 0.01
    )
);
