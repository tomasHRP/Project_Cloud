from flask import Flask, request, jsonify
import os
import time
import psycopg2
import psycopg2.extras

app = Flask(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "cloudapp"),
        user=os.getenv("DB_USER", "cloudadmin"),
        password=os.getenv("DB_PASSWORD", "cloudpassword")
    )


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
            print("Database initialized")
            return

        except Exception as error:
            print(f"Database not ready yet: {error}")
            time.sleep(3)

    raise Exception("Could not connect to database")


@app.get("/health")
def health():
    return jsonify({
        "service": "order-service",
        "status": "ok"
    })


@app.post("/orders")
def create_order():
    data = request.get_json()

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

    return jsonify(orders)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001)