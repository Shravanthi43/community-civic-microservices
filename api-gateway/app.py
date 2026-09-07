from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------
# API Gateway: single entry point for the frontend.
# It forwards requests to the microservice that owns the path.
# ---------------------------------------------------------------

CITIZEN_SERVICE_URL = "http://localhost:5001"
COMPLAINT_SERVICE_URL = "http://localhost:5002"
WARD_SERVICE_URL = "http://localhost:5003"


def forward_request(target_url, path):
    """Forward the incoming request to the target service."""

    url = f"{target_url}/{path}"

    try:
        response = requests.request(
            method=request.method,
            url=url,
            json=request.get_json(silent=True),
            params=request.args,
            timeout=5
        )

    except requests.exceptions.RequestException:
        return jsonify({
            "error": f"Service at {target_url} is unavailable"
        }), 503

    return Response(
        response.content,
        status=response.status_code,
        content_type=response.headers.get(
            "Content-Type",
            "application/json"
        )
    )


# ---------------------------------------------------------------
# Citizen Service
# Gateway: /citizens/*
# Backend: http://localhost:5001
# ---------------------------------------------------------------

@app.route(
    "/citizens",
    defaults={"path": ""},
    methods=["GET", "POST"]
)
@app.route(
    "/citizens/<path:path>",
    methods=["GET", "POST"]
)
def route_citizens(path):
    full_path = f"citizens/{path}" if path else "citizens"

    return forward_request(
        CITIZEN_SERVICE_URL,
        full_path
    )


# ---------------------------------------------------------------
# Complaint Service
# Gateway: /complaints/*
# Backend: http://localhost:5002
# ---------------------------------------------------------------

@app.route(
    "/complaints",
    defaults={"path": ""},
    methods=["GET", "POST"]
)
@app.route(
    "/complaints/<path:path>",
    methods=["GET", "POST"]
)
def route_complaints(path):
    full_path = f"complaints/{path}" if path else "complaints"

    return forward_request(
        COMPLAINT_SERVICE_URL,
        full_path
    )


# ---------------------------------------------------------------
# Ward Service
# Gateway: /wards/*
# Backend: http://localhost:5003
# ---------------------------------------------------------------

@app.route(
    "/wards",
    defaults={"path": ""},
    methods=["GET", "POST"]
)
@app.route(
    "/wards/<path:path>",
    methods=["GET", "POST"]
)
def route_wards(path):
    full_path = f"wards/{path}" if path else "wards"

    return forward_request(
        WARD_SERVICE_URL,
        full_path
    )


# ---------------------------------------------------------------
# Gateway health check
# ---------------------------------------------------------------

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "message": "API Gateway is running",
        "routes": {
            "/citizens/*": "Citizen Service (port 5001)",
            "/complaints/*": "Complaint Service (port 5002)",
            "/wards/*": "Ward Service (port 5003)"
        }
    })


if __name__ == "__main__":
    app.run(port=5000, debug=True)