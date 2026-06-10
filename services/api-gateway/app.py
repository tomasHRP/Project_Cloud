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
    })


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