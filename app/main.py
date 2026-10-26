"""
OrderService — a minimal microservice used as the deployable artifact
for the CI/CD pipeline case study.

Endpoints:
    GET  /health        -> liveness/readiness probe (used by staging & prod health checks)
    GET  /orders/<id>    -> fetch a single order
    POST /orders         -> create an order
"""

from flask import Flask, jsonify, request
import uuid

app = Flask(__name__)

# In-memory store standing in for a real database
ORDERS = {}


@app.get("/")
def index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OrderService Microservice</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background: #0f172a; color: #f8fafc; min-height: 100vh; padding: 2rem; display: flex; justify-content: center; }
        .container { max-width: 900px; width: 100%; display: flex; flex-direction: column; gap: 2rem; }
        .header { background: #1e293b; padding: 1.5rem 2rem; border-radius: 12px; border: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5rem; color: #38bdf8; display: flex; align-items: center; gap: 0.5rem; }
        .badge { background: #10b98122; color: #34d399; border: 1px solid #059669; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600; }
        .card { background: #1e293b; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; }
        .card h2 { font-size: 1.125rem; margin-bottom: 1rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
        .form-group { display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
        input { flex: 1; min-width: 200px; background: #0f172a; border: 1px solid #475569; border-radius: 8px; padding: 0.75rem 1rem; color: #fff; font-size: 1rem; outline: none; }
        input:focus { border-color: #38bdf8; }
        button { background: #0284c7; color: white; border: none; border-radius: 8px; padding: 0.75rem 1.5rem; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #0369a1; }
        .order-item { background: #0f172a; padding: 1rem; border-radius: 8px; border: 1px solid #334155; margin-bottom: 0.75rem; display: flex; justify-content: space-between; align-items: center; }
        .order-id { font-family: monospace; color: #38bdf8; font-size: 0.875rem; }
        .order-details { font-weight: 600; font-size: 1.1rem; }
        .empty { color: #64748b; text-align: center; padding: 2rem 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>📦 OrderService API</h1>
                <p style="color: #94a3b8; margin-top: 0.25rem;">CI/CD Microservice Case Study</p>
            </div>
            <span class="badge" id="health-badge">Checking...</span>
        </div>

        <div class="card">
            <h2>Create New Order</h2>
            <form id="orderForm">
                <div class="form-group">
                    <input type="text" id="itemInput" placeholder="Item Name (e.g. Laptop, Keyboard)" required>
                    <input type="number" id="qtyInput" placeholder="Quantity" min="1" value="1" required>
                    <button type="submit">Submit Order</button>
                </div>
            </form>
        </div>

        <div class="card">
            <h2>Active Orders</h2>
            <div id="ordersList"><div class="empty">No orders created yet. Use the form above to place an order.</div></div>
        </div>
    </div>

    <script>
        async function checkHealth() {
            try {
                const res = await fetch('/health');
                const data = await res.json();
                if(data.status === 'ok') {
                    document.getElementById('health-badge').innerText = '🟢 Service Healthy';
                }
            } catch {
                document.getElementById('health-badge').innerText = '🔴 Offline';
            }
        }

        async function loadOrders() {
            try {
                const res = await fetch('/orders');
                const orders = await res.json();
                const container = document.getElementById('ordersList');
                if(!Array.isArray(orders) || orders.length === 0) {
                    container.innerHTML = '<div class="empty">No orders created yet. Use the form above to place an order.</div>';
                    return;
                }
                container.innerHTML = orders.map(o => `
                    <div class="order-item">
                        <div>
                            <div class="order-details">${o.item} (x${o.quantity})</div>
                            <div class="order-id">ID: ${o.id}</div>
                        </div>
                        <span class="badge">${o.status}</span>
                    </div>
                `).join('');
            } catch(e) {}
        }

        document.getElementById('orderForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const item = document.getElementById('itemInput').value;
            const quantity = parseInt(document.getElementById('qtyInput').value);
            const res = await fetch('/orders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item, quantity })
            });
            if(res.ok) {
                document.getElementById('itemInput').value = '';
                document.getElementById('qtyInput').value = '1';
                loadOrders();
            }
        });

        checkHealth();
        loadOrders();
    </script>
</body>
</html>"""


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.get("/orders")
def list_orders():
    return jsonify(list(ORDERS.values())), 200


@app.post("/orders")
def create_order():
    payload = request.get_json(silent=True) or {}
    item = payload.get("item")
    quantity = payload.get("quantity")

    if not item or not isinstance(quantity, int) or quantity <= 0:
        return jsonify(error="item (str) and quantity (positive int) are required"), 400

    order_id = str(uuid.uuid4())
    ORDERS[order_id] = {
        "id": order_id,
        "item": item,
        "quantity": quantity,
        "status": "CREATED",
    }
    return jsonify(ORDERS[order_id]), 201


@app.get("/orders/<order_id>")
def get_order(order_id):
    order = ORDERS.get(order_id)
    if not order:
        return jsonify(error="order not found"), 404
    return jsonify(order), 200


if __name__ == "__main__":  # pragma: no cover
    print("\n==================================================")
    print(" 🚀 OrderService is running!")
    print(" -------------------------------------------------")
    print("  1. Dashboard UI : http://localhost:8080/")
    print("  2. Health API   : http://localhost:8080/health")
    print("  3. Orders API   : http://localhost:8080/orders")
    print("==================================================\n")
    app.run(host="0.0.0.0", port=8080)
