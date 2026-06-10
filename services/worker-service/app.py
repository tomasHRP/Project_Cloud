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
    print("Worker consumer started", flush=True)
    print(f"SQS_QUEUE_URL={SQS_QUEUE_URL}", flush=True)

    if not SQS_QUEUE_URL:
        print("SQS_QUEUE_URL not configured. Worker will not consume messages.", flush=True)
        return

    sqs = get_sqs_client()

    while True:
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
        "message": "Worker service ready for async processing"
    })


if __name__ == "__main__":
    thread = threading.Thread(target=consume_messages, daemon=True)
    thread.start()

    app.run(host="0.0.0.0", port=5002)