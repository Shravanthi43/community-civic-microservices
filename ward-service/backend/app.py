import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(
    os.path.dirname(__file__),
    "../database/ward.db"
)


def get_db():
    return sqlite3.connect(DATABASE)


def initialize_database():
    db = get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS wards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ward_number TEXT NOT NULL,
        ward_name TEXT NOT NULL,
        area TEXT NOT NULL
    )
    """)

    db.commit()
    db.close()


# ---------------------------------------------------------------
# Create Ward
# POST /wards
# ---------------------------------------------------------------

@app.route("/wards", methods=["POST"])
def create_ward():

    data = request.json

    ward_number = data["ward_number"]
    ward_name = data["ward_name"]
    area = data["area"]

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    INSERT INTO wards
    (ward_number, ward_name, area)
    VALUES (?, ?, ?)
    """, (ward_number, ward_name, area))

    db.commit()

    ward_id = cursor.lastrowid

    db.close()

    return jsonify({
        "ward_id": ward_id,
        "ward_number": ward_number,
        "ward_name": ward_name,
        "area": area
    }), 201


# ---------------------------------------------------------------
# Get All Wards
# GET /wards
# ---------------------------------------------------------------

@app.route("/wards", methods=["GET"])
def get_wards():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    SELECT id, ward_number, ward_name, area
    FROM wards
    """)

    wards = cursor.fetchall()

    db.close()

    result = []

    for ward in wards:
        result.append({
            "ward_id": ward[0],
            "ward_number": ward[1],
            "ward_name": ward[2],
            "area": ward[3]
        })

    return jsonify(result)


# ---------------------------------------------------------------
# Get Single Ward
# GET /wards/<id>
# ---------------------------------------------------------------

@app.route("/wards/<int:ward_id>", methods=["GET"])
def get_ward(ward_id):

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    SELECT id, ward_number, ward_name, area
    FROM wards
    WHERE id = ?
    """, (ward_id,))

    ward = cursor.fetchone()

    db.close()

    if ward is None:
        return jsonify({
            "error": "Ward not found"
        }), 404

    return jsonify({
        "ward_id": ward[0],
        "ward_number": ward[1],
        "ward_name": ward[2],
        "area": ward[3]
    })


# ---------------------------------------------------------------
# Start Ward Service
# ---------------------------------------------------------------


# Validate Ward by Ward Number
@app.route("/wards/number/<ward_number>", methods=["GET"])
def get_ward_by_number(ward_number):

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id, ward_number, ward_name, area
        FROM wards
        WHERE ward_number = ?
    """, (ward_number,))

    ward = cursor.fetchone()

    db.close()

    if ward is None:
        return jsonify({
            "error": "Ward not found"
        }), 404

    return jsonify({
        "ward_id": ward[0],
        "ward_number": ward[1],
        "ward_name": ward[2],
        "area": ward[3]
    })

if __name__ == "__main__":
    initialize_database()
    app.run(port=int(sys.argv[1]) if len(sys.argv) > 1 else 5003, debug=True)