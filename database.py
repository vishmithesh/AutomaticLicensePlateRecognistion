
import sqlite3
import os

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(
    BASE_DIR,
    "db_storage",
    "traffic.db"
)


# Create database and table
def create_table():

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT NOT NULL,
                capture_date TEXT NOT NULL,
                capture_time TEXT NOT NULL,
                confidence REAL,
                image_filename TEXT NOT NULL,
                image_path TEXT NOT NULL
            )
        """)

        # Check existing columns
        columns = [
            row[1] for row in connection.execute(
                "PRAGMA table_info(vehicle_records)"
            )
        ]

        # Add location column if missing
        if "location" not in columns:
            connection.execute("""
                ALTER TABLE vehicle_records
                ADD COLUMN location TEXT
            """)

        connection.commit()
        print("Database table created successfully")

    finally:
        connection.close()


# Insert vehicle record
def insert_vehicle(
    plate,
    date,
    time,
    confidence,
    filename,
    image_path,
    location="Coimbatore"
):

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO vehicle_records (
                plate_number,
                capture_date,
                capture_time,
                confidence,
                image_filename,
                image_path,
                location
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(plate),
            str(date),
            str(time),
            float(confidence),
            str(filename),
            str(image_path),
            str(location)
        ))

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


# Retrieve all records
def get_all_records():

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.row_factory = sqlite3.Row

        records = connection.execute("""
            SELECT *
            FROM vehicle_records
            ORDER BY id DESC
        """).fetchall()

        return records

    finally:
        connection.close()


# Get total vehicles
def get_total_vehicles():

    connection = sqlite3.connect(DB_PATH)

    try:
        result = connection.execute("""
            SELECT COUNT(*)
            FROM vehicle_records
        """).fetchone()

        return result[0]

    finally:
        connection.close()


# Get today's detections
def get_today_vehicles():

    connection = sqlite3.connect(DB_PATH)

    try:
        result = connection.execute("""
            SELECT COUNT(*)
            FROM vehicle_records
            WHERE capture_date = date('now', 'localtime')
        """).fetchone()

        return result[0]

    finally:
        connection.close()


# Run database setup
if __name__ == "__main__":

    create_table()

    print("Database location:", DB_PATH)
    print("Total vehicles:", get_total_vehicles())
    print("Today's vehicles:", get_today_vehicles())
