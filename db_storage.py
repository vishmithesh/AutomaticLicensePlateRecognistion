
from flask import Flask, render_template_string, send_from_directory, abort
from database import get_all_records
import os

app = Flask(__name__)

# Folder containing captured vehicle images
CAPTURE_FOLDER = os.path.abspath("captures")


# Dashboard HTML and CSS
HTML = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>ANPR Traffic Signal Dashboard</title>

    <meta http-equiv="refresh" content="5">

    <style>

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            padding: 30px;
            color: #1e293b;
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

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }

        .card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .card h3 {
            color: #64748b;
            font-size: 15px;
            margin-bottom: 12px;
        }

        .card h2 {
            font-size: 30px;
            color: #172554;
        }

        .section {
            background: white;
            padding: 25px;
            border-radius: 12px;
            overflow-x: auto;
        }

        .section h2 {
            margin-bottom: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 750px;
        }

        th, td {
            padding: 14px;
            border-bottom: 1px solid #e2e8f0;
            text-align: center;
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

        .image-link {
            display: inline-block;
            background: #2563eb;
            color: white;
            padding: 8px 13px;
            border-radius: 6px;
            text-decoration: none;
        }

        .image-link:hover {
            background: #1d4ed8;
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

    <header>
        <h1>ANPR IoT Traffic Signal Dashboard</h1>
        <p>Automatic Number Plate Recognition and Vehicle Monitoring System</p>
    </header>


    <!-- Statistics -->

    <div class="dashboard">

        <div class="card">
            <h3>Total Vehicles Detected</h3>
            <h2>{{ records|length }}</h2>
        </div>

        <div class="card">
            <h3>Latest Number Plate</h3>
            <h2 style="font-size:22px">
                {% if records %}
                    {{ records[0]['plate_number'] }}
                {% else %}
                    ---
                {% endif %}
            </h2>
        </div>

        <div class="card">
            <h3>System Status</h3>
            <h2 style="font-size:22px;color:#16a34a">
                ONLINE
            </h2>
        </div>

    </div>


    <!-- Vehicle Records -->

    <div class="section">

        <h2>Vehicle Detection Records</h2>

        {% if records %}

        <table>

            <thead>
                <tr>
                    <th>ID</th>
                    <th>Number Plate</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Confidence</th>
                    <th>Captured Image</th>
                </tr>
            </thead>

            <tbody>

                {% for record in records %}

                <tr>

                    <td>{{ record['id'] }}</td>

                    <td class="plate">
                        {{ record['plate_number'] }}
                    </td>

                    <td>
                        {{ record['capture_date'] }}
                    </td>

                    <td>
                        {{ record['capture_time'] }}
                    </td>

                    <td>
                        {{ "%.2f"|format(record['confidence']) }}
                    </td>

                    <td>
                        <a class="image-link"
                           href="/captures/{{ record['image_filename'] }}"
                           target="_blank">
                           View Image
                        </a>
                    </td>

                </tr>

                {% endfor %}

            </tbody>

        </table>

        {% else %}

        <div class="empty">
            <h3>No Vehicle Records Found</h3>
            <p>Waiting for number plate detection...</p>
        </div>

        {% endif %}

    </div>


    <footer>
        ANPR IoT Traffic Signal Control System
        <br>
        Dashboard automatically refreshes every 5 seconds.
    </footer>

</body>
</html>
"""


# Home page
@app.route("/")
def home():

    try:
        records = get_all_records()

        return render_template_string(
            HTML,
            records=records
        )

    except Exception as error:

        return f"""
        <h2>Dashboard Database Error</h2>
        <p>{str(error)}</p>
        <p>Check database.py and database/traffic.db</p>
        """, 500


# Display captured vehicle images
@app.route("/captures/<path:filename>")
def captured_image(filename):

    # Prevent access to files outside the captures folder
    if os.path.basename(filename) != filename:
        abort(404)

    return send_from_directory(
        CAPTURE_FOLDER,
        filename
    )


# Start Flask server
def start_dashboard():

    print("----------------------------------")
    print("ANPR TRAFFIC DASHBOARD")
    print("----------------------------------")
    print("Dashboard URL: http://127.0.0.1:5000")
    print("Waiting for vehicle records...")
    print("----------------------------------")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )


# Execute when dashboard.py is run directly
if __name__ == "__main__":
    start_dashboard()
