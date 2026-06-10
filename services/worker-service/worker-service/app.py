from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({
        "service": "worker-service",
        "status": "ok",
        "message": "Worker service ready for async processing"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)