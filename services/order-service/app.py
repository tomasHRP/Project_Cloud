from flask import Flask, request, jsonify
import os
import time
import json
import boto3
import psycopg2
import psycopg2.extras

app = Flask(__name__)

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
LOCAL_MODE = os.getenv("LOCAL_MODE", "false").lower() == "true"


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "cloudapp"),
        user=os.getenv("DB_USER", "cloudadmin"),
        password=os.getenv("DB_PASSWORD", "cloudpassword")
    )


def get_sqs_client():
    return boto3.client("sqs", region_name=AWS_REGION)


def init_db():
    retries = 10

    for attempt in range(retries):
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    product_name VARCHAR(255) NOT NULL,
                    quantity INTEGER NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.commit()
            cur.close()
            conn.close()

            print("Database initialized", flush=True)
            return

        except Exception as error:
            print(f"Database not ready yet. Attempt {attempt + 1}/{retries}: {error}", flush=True)
            time.sleep(3)

    raise Exception("Could not connect to database")


@app.get("/health")
def health():
    return jsonify({
        "service": "order-service",
        "status": "ok"
    }), 200


@app.get("/ready")
def ready():
    checks = {
        "database": "unknown",
        "local_mode": LOCAL_MODE,
        "sqs": "disabled_local_mode" if LOCAL_MODE else ("configured" if SQS_QUEUE_URL else "not_configured")
    }

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()

        checks["database"] = "connected"

        return jsonify({
            "service": "order-service",
            "status": "ready",
            "checks": checks
        }), 200

    except Exception as error:
        checks["database"] = "unreachable"

        return jsonify({
            "service": "order-service",
            "status": "not_ready",
            "checks": checks,
            "error": str(error)
        }), 503


@app.post("/orders")
def create_order():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    product_name = data.get("product_name")
    quantity = data.get("quantity")

    if not product_name or not quantity:
        return jsonify({
            "error": "product_name and quantity are required"
        }), 400

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        INSERT INTO orders (product_name, quantity, status)
        VALUES (%s, %s, %s)
        RETURNING id, product_name, quantity, status, created_at;
    """, (product_name, quantity, "PENDING"))

    order = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    if LOCAL_MODE:
        print(f"LOCAL_MODE=true. Order {order['id']} created locally. Message not sent to SQS.", flush=True)

    elif SQS_QUEUE_URL:
        try:
            sqs = get_sqs_client()

            message = {
                "order_id": order["id"],
                "product_name": order["product_name"],
                "quantity": order["quantity"]
            }

            sqs.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps(message)
            )

            print(f"Message sent to SQS for order {order['id']}", flush=True)

        except Exception as error:
            print(f"Failed to send message to SQS: {error}", flush=True)

    else:
        print("SQS_QUEUE_URL not configured. Message not sent.", flush=True)

    return jsonify(order), 201


@app.get("/orders")
def list_orders():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT id, product_name, quantity, status, created_at
        FROM orders
        ORDER BY id DESC;
    """)

    orders = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(orders), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001)