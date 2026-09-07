from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import time
from collections import defaultdict, deque

app = Flask(__name__)
CORS(app)

# ============================================================
# MICROSERVICE INSTANCES
# ============================================================

CITIZEN_SERVICES = [
    "http://localhost:5001",
    "http://localhost:5004"
]

COMPLAINT_SERVICES = [
    "http://localhost:5002",
    "http://localhost:5005"
]

WARD_SERVICES = [
    "http://localhost:5003",
    "http://localhost:5006"
]

# Round-robin counters
counters = {
    "citizen": 0,
    "complaint": 0,
    "ward": 0
}

# ============================================================
# RATE LIMITING
# ============================================================

RATE_LIMIT = 100
WINDOW = 60

request_history = defaultdict(deque)


def check_rate_limit(client_ip):

    now = time.time()
    history = request_history[client_ip]

    while history and history[0] <= now - WINDOW:
        history.popleft()

    if len(history) >= RATE_LIMIT:
        return False

    history.append(now)
    return True


# ============================================================
# LOAD BALANCING - ROUND ROBIN
# ============================================================

def get_next_service(service_name, services):

    index = counters[service_name]

    service = services[index]

    counters[service_name] = (
        index + 1
    ) % len(services)

    return service


# ============================================================
# LOGGING & MONITORING
# ============================================================

def log_request(method, path, service, status, response_time):

    print(
        f"[GATEWAY LOG] "
        f"{method} {path} -> {service} | "
        f"Status: {status} | "
        f"Time: {response_time:.3f}s"
    )


# ============================================================
# FORWARD REQUEST
# ============================================================

def forward_request(service_name, services, path):

    client_ip = request.remote_addr

    # Rate Limiting
    if not check_rate_limit(client_ip):

        return jsonify({
            "error": "Rate limit exceeded",
            "message": "Maximum 100 requests per minute allowed"
        }), 429


    # Load Balancing
    attempts = len(services)

    for _ in range(attempts):

        service_url = get_next_service(
            service_name,
            services
        )

        url = f"{service_url}/{path}"

        start_time = time.time()

        try:

            response = requests.request(
                method=request.method,
                url=url,
                json=request.get_json(silent=True),
                params=request.args,
                timeout=5
            )

            response_time = time.time() - start_time

            log_request(
                request.method,
                request.path,
                service_url,
                response.status_code,
                response_time
            )

            return Response(
                response.content,
                status=response.status_code,
                content_type=response.headers.get(
                    "Content-Type",
                    "application/json"
                )
            )

        except requests.exceptions.RequestException:

            response_time = time.time() - start_time

            log_request(
                request.method,
                request.path,
                service_url,
                "UNAVAILABLE",
                response_time
            )

    return jsonify({
        "error": f"{service_name.capitalize()} Service is unavailable"
    }), 503


# ============================================================
# CITIZEN ROUTE
# ============================================================

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

    full_path = (
        f"citizens/{path}"
        if path
        else "citizens"
    )

    return forward_request(
        "citizen",
        CITIZEN_SERVICES,
        full_path
    )


# ============================================================
# COMPLAINT ROUTE
# ============================================================

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

    full_path = (
        f"complaints/{path}"
        if path
        else "complaints"
    )

    return forward_request(
        "complaint",
        COMPLAINT_SERVICES,
        full_path
    )


# ============================================================
# WARD ROUTE
# ============================================================

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

    full_path = (
        f"wards/{path}"
        if path
        else "wards"
    )

    return forward_request(
        "ward",
        WARD_SERVICES,
        full_path
    )


# ============================================================
# GATEWAY HEALTH CHECK
# ============================================================

@app.route("/", methods=["GET"])
def health_check():

    return jsonify({
        "message": "API Gateway is running",
        "port": 5000,
        "services": {
            "citizen": CITIZEN_SERVICES,
            "complaint": COMPLAINT_SERVICES,
            "ward": WARD_SERVICES
        },
        "responsibilities": [
            "Request Routing",
            "Load Balancing",
            "Rate Limiting",
            "Logging and Monitoring"
        ]
    })


# ============================================================
# START API GATEWAY
# ============================================================

if __name__ == "__main__":

    app.run(
        port=5000,
        debug=True
    )
