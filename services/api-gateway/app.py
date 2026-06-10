from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:5001")


@app.get("/health")
def health():
    return jsonify({
        "service": "api-gateway",
        "status": "ok"
    }), 200


@app.get("/ready")
def ready():
    try:
        response = requests.get(f"{ORDER_SERVICE_URL}/health", timeout=3)

        if response.status_code == 200:
            return jsonify({
                "service": "api-gateway",
                "status": "ready",
                "order_service": "reachable"
            }), 200

        return jsonify({
            "service": "api-gateway",
            "status": "not_ready",
            "order_service": "unhealthy",
            "order_service_status_code": response.status_code
        }), 503

    except Exception as error:
        return jsonify({
            "service": "api-gateway",
            "status": "not_ready",
            "order_service": "unreachable",
            "error": str(error)
        }), 503


@app.post("/orders")
def create_order():
    response = requests.post(
        f"{ORDER_SERVICE_URL}/orders",
        json=request.get_json()
    )
    return jsonify(response.json()), response.status_code


@app.get("/orders")
def list_orders():
    response = requests.get(f"{ORDER_SERVICE_URL}/orders")
    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)