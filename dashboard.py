
import os
import csv
import io
import sqlite3

from flask import (
    Flask,
    request,
    render_template_string,
    send_from_directory,
    Response
)

from database import (
    DB_PATH,
    create_table,
    get_total_vehicles,
    get_today_vehicles
)


# --------------------------------------------------
# 1. APPLICATION CONFIGURATION
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CAPTURE_FOLDER = os.path.join(BASE_DIR, "captures")

app = Flask(__name__)

os.makedirs(CAPTURE_FOLDER, exist_ok=True)

# Ensure database and required table exist
create_table()


# --------------------------------------------------
# 2. DATABASE CONNECTION
# --------------------------------------------------

def get_connection():

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    return connection


# --------------------------------------------------
# 3. HTML DASHBOARD DESIGN
# --------------------------------------------------

HTML = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>ALPR Monitoring Dashboard</title>

    <style>

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }

        body {
            background: #f1f5f9;
            color: #1e293b;
            padding: 25px;
        }

        .container {
            max-width: 1450px;
            margin: auto;
        }

        header {
            background: #172554;
            color: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
        }

        header h1 {
            margin-bottom: 8px;
        }

        header p {
            color: #cbd5e1;
        }

        .stats {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(200px, 1fr));
            gap: 18px;
            margin-bottom: 25px;
        }

        .card {
            background: white;
            padding: 22px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }

        .card h3 {
            color: #64748b;
            font-size: 14px;
            margin-bottom: 12px;
        }

        .card h2 {
            font-size: 28px;
            color: #1d4ed8;
        }

        .filter-section {
            background: white;
            padding: 22px;
            border-radius: 12px;
            margin-bottom: 25px;
        }

        .filter-section h2 {
            margin-bottom: 18px;
        }

        .filter-grid {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
        }

        label {
            display: block;
            font-weight: bold;
            font-size: 13px;
            margin-bottom: 7px;
        }

        input, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            outline: none;
        }

        input:focus, select:focus {
            border-color: #2563eb;
        }

        .actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 18px;
        }

        button, .button {
            padding: 11px 18px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            font-weight: bold;
            display: inline-block;
        }

        .apply {
            background: #2563eb;
            color: white;
        }

        .clear {
            background: #64748b;
            color: white;
        }

        .export {
            background: #15803d;
            color: white;
        }

        .table-section {
            background: white;
            padding: 22px;
            border-radius: 12px;
            overflow-x: auto;
        }

        .table-section h2 {
            margin-bottom: 18px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 950px;
        }

        th, td {
            padding: 13px;
            text-align: center;
            border-bottom: 1px solid #e2e8f0;
        }

        th {
            background: #172554;
            color: white;
        }

        tr:hover {
            background: #f8fafc;
        }

        .plate {
            font-weight: bold;
            color: #1d4ed8;
        }

        .confidence {
            color: #15803d;
            font-weight: bold;
        }

        .vehicle-image {
            width: 110px;
            height: 70px;
            object-fit: cover;
            border-radius: 6px;
        }

        .empty {
            padding: 30px;
            text-align: center;
            color: #64748b;
        }

        footer {
            text-align: center;
            margin-top: 25px;
            color: #64748b;
            font-size: 13px;
        }

    </style>

</head>

<body>

<div class="container">

    <header>

        <h1>Automatic License Plate Recognition</h1>

        <p>
            ALPR Vehicle Monitoring and Detection Dashboard
        </p>

        <p>
            Location: Coimbatore
        </p>

    </header>


    <!-- STATISTICS -->

    <section class="stats">

        <div class="card">

            <h3>Total Vehicles Detected</h3>

            <h2>{{ total_vehicles }}</h2>

        </div>


        <div class="card">

            <h3>Today's Detections</h3>

            <h2>{{ today_vehicles }}</h2>

        </div>


        <div class="card">

            <h3>Filtered Records</h3>

            <h2>{{ records|length }}</h2>

        </div>


        <div class="card">

            <h3>Average OCR Confidence</h3>

            <h2>{{ average_confidence }}%</h2>

        </div>

    </section>


    <!-- FILTER SECTION -->

    <section class="filter-section">

        <h2>Search and Filter Vehicle Records</h2>

        <form method="GET" action="/">

            <div class="filter-grid">

                <div>

                    <label>Vehicle Number</label>

                    <input
                        type="text"
                        name="plate"
                        placeholder="TN37AB1234"
                        value="{{ filters.plate }}"
                    >

                </div>


                <div>

                    <label>Start Date</label>

                    <input
                        type="date"
                        name="start_date"
                        value="{{ filters.start_date }}"
                    >

                </div>


                <div>

                    <label>End Date</label>

                    <input
                        type="date"
                        name="end_date"
                        value="{{ filters.end_date }}"
                    >

                </div>


                <div>

                    <label>Start Time</label>

                    <input
                        type="time"
                        name="start_time"
                        value="{{ filters.start_time }}"
                    >

                </div>


                <div>

                    <label>End Time</label>

                    <input
                        type="time"
                        name="end_time"
                        value="{{ filters.end_time }}"
                    >

                </div>


                <div>

                    <label>Location</label>

                    <input
                        type="text"
                        name="location"
                        placeholder="Coimbatore"
                        value="{{ filters.location }}"
                    >

                </div>


                <div>

                    <label>Minimum Confidence (%)</label>

                    <input
                        type="number"
                        name="min_conf"
                        min="0"
                        max="100"
                        step="1"
                        value="{{ filters.min_conf }}"
                    >

                </div>


                <div>

                    <label>Sort Records</label>

                    <select name="sort">

                        <option value="newest"
                            {% if filters.sort == "newest" %}
                            selected
                            {% endif %}>
                            Newest First
                        </option>

                        <option value="oldest"
                            {% if filters.sort == "oldest" %}
                            selected
                            {% endif %}>
                            Oldest First
                        </option>

                        <option value="plate"
                            {% if filters.sort == "plate" %}
                            selected
                            {% endif %}>
                            Plate Number
                        </option>

                        <option value="confidence"
                            {% if filters.sort == "confidence" %}
                            selected
                            {% endif %}>
                            Highest Confidence
                        </option>

                    </select>

                </div>

            </div>


            <div class="actions">

                <button class="apply" type="submit">
                    Apply Filters
                </button>

                <a href="/" class="button clear">
                    Clear Filters
                </a>

                <a href="/export?{{ request.query_string.decode('utf-8') }}"
                   class="button export">
                    Export CSV
                </a>

            </div>

        </form>

    </section>


    <!-- VEHICLE RECORDS -->

    <section class="table-section">

        <h2>Detected Vehicle Records</h2>

        <table>

            <thead>

                <tr>

                    <th>ID</th>

                    <th>Plate Number</th>

                    <th>Date</th>

                    <th>Time</th>

                    <th>Location</th>

                    <th>Confidence</th>

                    <th>Captured Image</th>

                </tr>

            </thead>


            <tbody>

                {% for record in records %}

                <tr>

                    <td>{{ record.id }}</td>

                    <td class="plate">
                        {{ record.plate_number }}
                    </td>

                    <td>{{ record.capture_date }}</td>

                    <td>{{ record.capture_time }}</td>

                    <td>{{ record.location or "Coimbatore" }}</td>

                    <td class="confidence">
                        {{ "%.2f"|format(record.confidence or 0) }}%
                    </td>

                    <td>

                        {% if record.image_filename %}

                        <a
                            href="/captures/{{ record.image_filename }}"
                            target="_blank"
                        >

                            <img
                                class="vehicle-image"
                                src="/captures/{{ record.image_filename }}"
                                alt="Vehicle capture"
                            >

                        </a>

                        {% else %}

                        No Image

                        {% endif %}

                    </td>

                </tr>

                {% else %}

                <tr>

                    <td colspan="7" class="empty">
                        No vehicle records found.
                    </td>

                </tr>

                {% endfor %}

            </tbody>

        </table>

    </section>


    <footer>

        Automatic License Plate Recognition System |
        Python + OpenCV + EasyOCR + ESP32 + SQLite + Flask

    </footer>

</div>

</body>

</html>
"""


# --------------------------------------------------
# 4. FILTER AND SORT RECORDS
# --------------------------------------------------

def get_filtered_records(filters):

    conditions = []

    values = []


    # Vehicle number search

    plate = filters.get("plate", "").strip().upper()

    if plate:

        conditions.append("UPPER(plate_number) LIKE ?")

        values.append("%" + plate + "%")


    # Start date

    start_date = filters.get("start_date", "").strip()

    if start_date:

        conditions.append("capture_date >= ?")

        values.append(start_date)


    # End date

    end_date = filters.get("end_date", "").strip()

    if end_date:

        conditions.append("capture_date <= ?")

        values.append(end_date)


    # Start time

    start_time = filters.get("start_time", "").strip()

    if start_time:

        conditions.append("capture_time >= ?")

        values.append(start_time + ":00"
                      if len(start_time) == 5 else start_time)


    # End time

    end_time = filters.get("end_time", "").strip()

    if end_time:

        conditions.append("capture_time <= ?")

        values.append(end_time + ":59"
                      if len(end_time) == 5 else end_time)


    # Location

    location = filters.get("location", "").strip()

    if location:

        conditions.append("location LIKE ?")

        values.append("%" + location + "%")


    # Minimum OCR confidence

    min_conf = filters.get("min_conf", "").strip()

    if min_conf:

        try:

            confidence_value = float(min_conf)

            if not 0 <= confidence_value <= 100:
                raise ValueError("Confidence must be between 0 and 100")

            conditions.append("confidence >= ?")

            values.append(confidence_value)

        except ValueError:

            raise ValueError(
                "Minimum confidence must be a number between 0 and 100"
            )


    # Build WHERE clause

    where_clause = ""

    if conditions:

        where_clause = "WHERE " + " AND ".join(conditions)


    # Safe sorting

    sort_options = {

        "newest": "id DESC",

        "oldest": "id ASC",

        "plate": "plate_number ASC",

        "confidence": "confidence DESC"

    }

    sort = filters.get("sort", "newest")

    order_clause = sort_options.get(sort, "id DESC")


    query = f"""

        SELECT *

        FROM vehicle_records

        {where_clause}

        ORDER BY {order_clause}

    """


    connection = get_connection()

    try:

        records = connection.execute(
            query,
            values
        ).fetchall()

        return records

    finally:

        connection.close()


# --------------------------------------------------
# 5. MAIN DASHBOARD ROUTE
# --------------------------------------------------

@app.route("/", methods=["GET"])

def dashboard():

    filters = {

        "plate": request.args.get("plate", ""),

        "start_date": request.args.get("start_date", ""),

        "end_date": request.args.get("end_date", ""),

        "start_time": request.args.get("start_time", ""),

        "end_time": request.args.get("end_time", ""),

        "location": request.args.get("location", ""),

        "min_conf": request.args.get("min_conf", ""),

        "sort": request.args.get("sort", "newest")

    }


    try:

        records = get_filtered_records(filters)

        total_vehicles = get_total_vehicles()

        today_vehicles = get_today_vehicles()

        if records:

            average = sum(
                float(record["confidence"] or 0)
                for record in records
            ) / len(records)

        else:

            average = 0


        return render_template_string(

            HTML,

            records=records,

            total_vehicles=total_vehicles,

            today_vehicles=today_vehicles,

            average_confidence=round(average, 2),

            filters=filters

        )


    except (sqlite3.Error, ValueError) as error:

        app.logger.exception("Dashboard error")

        return (
            "Dashboard error: " + str(error),
            500
        )


# --------------------------------------------------
# 6. DISPLAY CAPTURED IMAGES
# --------------------------------------------------

@app.route("/captures/<path:filename>")

def show_capture(filename):

    return send_from_directory(
        CAPTURE_FOLDER,
        filename
    )


# --------------------------------------------------
# 7. EXPORT RECORDS TO CSV
# --------------------------------------------------

@app.route("/export")

def export_csv():

    filters = {

        "plate": request.args.get("plate", ""),

        "start_date": request.args.get("start_date", ""),

        "end_date": request.args.get("end_date", ""),

        "start_time": request.args.get("start_time", ""),

        "end_time": request.args.get("end_time", ""),

        "location": request.args.get("location", ""),

        "min_conf": request.args.get("min_conf", ""),

        "sort": request.args.get("sort", "newest")

    }


    try:

        records = get_filtered_records(filters)

        output = io.StringIO()

        writer = csv.writer(output)

        writer.writerow([

            "ID",

            "Plate Number",

            "Capture Date",

            "Capture Time",

            "Location",

            "Confidence",

            "Image Filename",

            "Image Path"

        ])


        for record in records:

            writer.writerow([

                record["id"],

                record["plate_number"],

                record["capture_date"],

                record["capture_time"],

                record["location"],

                record["confidence"],

                record["image_filename"],

                record["image_path"]

            ])


        response = Response(

            output.getvalue(),

            mimetype="text/csv"

        )

        response.headers["Content-Disposition"] = (
            "attachment; filename=vehicle_records.csv"
        )

        return response


    except (sqlite3.Error, ValueError) as error:

        app.logger.exception("CSV export error")

        return (
            "Export error: " + str(error),
            500
        )


# --------------------------------------------------
# 8. START FLASK SERVER
# --------------------------------------------------

def start_dashboard():

    print("Starting ALPR Dashboard...")

    print("Database:", DB_PATH)

    print("Dashboard URL: http://127.0.0.1:5000")

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=False,

        use_reloader=False

    )


if __name__ == "__main__":

    start_dashboard()
