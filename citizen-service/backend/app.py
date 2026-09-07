from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import requests

app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(
    os.path.dirname(__file__),
    "../database/citizen.db"
)

# Ward Service
WARD_SERVICE_URL = "http://localhost:5003"


def get_db():
    return sqlite3.connect(DATABASE)


def initialize_database():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS citizens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ward TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    db.commit()
    db.close()


# ---------------------------------------------------------------
# Register Citizen
# Citizen Service first checks Ward Service
# ---------------------------------------------------------------

@app.route("/citizens", methods=["POST"])
def create_citizen():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    name = data.get("name")
    ward = data.get("ward")
    phone = data.get("phone")

    if not name or not ward or not phone:
        return jsonify({
            "error": "name, ward and phone are required"
        }), 400


    # -----------------------------------------------------------
    # STEP 1: Check Ward Service
    # -----------------------------------------------------------

    try:

        ward_response = requests.get(
            f"{WARD_SERVICE_URL}/wards/number/{ward}",
            timeout=5
        )

    except requests.exceptions.RequestException:

        return jsonify({
            "error": "Ward Service is unavailable"
        }), 503


    # -----------------------------------------------------------
    # STEP 2: Ward does not exist
    # -----------------------------------------------------------

    if ward_response.status_code == 404:

        return jsonify({
            "error": "Ward does not exist"
        }), 400


    # -----------------------------------------------------------
    # STEP 3: Other Ward Service error
    # -----------------------------------------------------------

    if ward_response.status_code != 200:

        return jsonify({
            "error": "Unable to validate ward"
        }), 503


    # -----------------------------------------------------------
    # STEP 4: Ward exists → Register Citizen
    # -----------------------------------------------------------

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO citizens (name, ward, phone)
        VALUES (?, ?, ?)
    """, (name, ward, phone))

    db.commit()

    citizen_id = cursor.lastrowid

    db.close()


    return jsonify({
        "message": "Citizen registered successfully",
        "citizen_id": citizen_id,
        "name": name,
        "ward": ward,
        "phone": phone
    }), 201


# ---------------------------------------------------------------
# Get Citizen
# ---------------------------------------------------------------

@app.route("/citizens/<int:citizen_id>", methods=["GET"])
def get_citizen(citizen_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id, name, ward, phone
        FROM citizens
        WHERE id = ?
    """, (citizen_id,))

    citizen = cursor.fetchone()

    db.close()

    if citizen is None:

        return jsonify({
            "error": "Citizen not found"
        }), 404

    return jsonify({
        "citizen_id": citizen[0],
        "name": citizen[1],
        "ward": citizen[2],
        "phone": citizen[3]
    })


# ---------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------

@app.route("/", methods=["GET"])
def health_check():

    return jsonify({
        "message": "Citizen Service is running",
        "port": 5001,
        "ward_validation": "enabled"
    })


# ---------------------------------------------------------------
# Start Citizen Service
# ---------------------------------------------------------------

if __name__ == "__main__":

    initialize_database()

    app.run(
        port=5001,
        debug=True
    )
