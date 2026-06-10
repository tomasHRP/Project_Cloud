from flask import Flask, jsonify
import os
import json
import time
import threading
import boto3
import psycopg2

app = Flask(__name__)

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
LOCAL_MODE = os.getenv("LOCAL_MODE", "false").lower() == "true"

worker_started = False
last_worker_heartbeat = None


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


def process_order(order_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE orders
        SET status = 'PROCESSED'
        WHERE id = %s;
    """, (order_id,))

    conn.commit()
    cur.close()
    conn.close()

    print(f"Order {order_id} processed", flush=True)


def consume_messages():
    global worker_started
    global last_worker_heartbeat

    worker_started = True
    last_worker_heartbeat = time.time()

    print("Worker consumer started", flush=True)
    print(f"LOCAL_MODE={LOCAL_MODE}", flush=True)
    print(f"SQS_QUEUE_URL={SQS_QUEUE_URL}", flush=True)

    if LOCAL_MODE:
        print("LOCAL_MODE=true. Worker will not consume SQS locally.", flush=True)

        while True:
            last_worker_heartbeat = time.time()
            print("Worker running in local mode.", flush=True)
            time.sleep(30)

    if not SQS_QUEUE_URL:
        print("SQS_QUEUE_URL not configured. Worker will not consume messages.", flush=True)

        while True:
            last_worker_heartbeat = time.time()
            print("Worker running but SQS is not configured.", flush=True)
            time.sleep(30)

    sqs = get_sqs_client()

    while True:
        last_worker_heartbeat = time.time()

        try:
            response = sqs.receive_message(
                QueueUrl=SQS_QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10
            )

            messages = response.get("Messages", [])

            for message in messages:
                print(f"Received message: {message['Body']}", flush=True)

                body = json.loads(message["Body"])
                order_id = body["order_id"]

                process_order(order_id)

                sqs.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=message["ReceiptHandle"]
                )

                print(f"Message for order {order_id} deleted from SQS", flush=True)

        except Exception as error:
            print(f"Worker error: {error}", flush=True)

        time.sleep(2)


@app.get("/health")
def health():
    return jsonify({
        "service": "worker-service",
        "status": "ok",
        "message": "Worker service running"
    }), 200


@app.get("/ready")
def ready():
    checks = {
        "database": "unknown",
        "local_mode": LOCAL_MODE,
        "sqs": "disabled_local_mode" if LOCAL_MODE else ("configured" if SQS_QUEUE_URL else "not_configured"),
        "worker_thread": "started" if worker_started else "not_started",
        "last_worker_heartbeat": last_worker_heartbeat
    }

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()

        checks["database"] = "connected"

        if not worker_started:
            return jsonify({
                "service": "worker-service",
                "status": "not_ready",
                "checks": checks
            }), 503

        if not LOCAL_MODE and not SQS_QUEUE_URL:
            return jsonify({
                "service": "worker-service",
                "status": "not_ready",
                "checks": checks
            }), 503

        return jsonify({
            "service": "worker-service",
            "status": "ready",
            "checks": checks
        }), 200

    except Exception as error:
        checks["database"] = "unreachable"

        return jsonify({
            "service": "worker-service",
            "status": "not_ready",
            "checks": checks,
            "error": str(error)
        }), 503


if __name__ == "__main__":
    thread = threading.Thread(target=consume_messages, daemon=True)
    thread.start()

    app.run(host="0.0.0.0", port=5002)