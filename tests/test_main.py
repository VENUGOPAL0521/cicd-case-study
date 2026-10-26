import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

import pytest
from main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Pipeline health-check stage relies on this contract."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_create_order_success(client):
    resp = client.post("/orders", json={"item": "Laptop", "quantity": 2})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["item"] == "Laptop"
    assert body["quantity"] == 2
    assert body["status"] == "CREATED"
    assert "id" in body


def test_create_order_missing_fields(client):
    resp = client.post("/orders", json={"item": "Laptop"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_create_order_invalid_quantity(client):
    resp = client.post("/orders", json={"item": "Laptop", "quantity": -5})
    assert resp.status_code == 400


def test_get_order_success(client):
    create_resp = client.post("/orders", json={"item": "Monitor", "quantity": 1})
    order_id = create_resp.get_json()["id"]

    get_resp = client.get(f"/orders/{order_id}")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["item"] == "Monitor"


def test_get_order_not_found(client):
    resp = client.get("/orders/does-not-exist")
    assert resp.status_code == 404
def test_dashboard_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"OrderService Microservice" in response.data
    assert b"<html" in response.data
def test_dashboard_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"OrderService Microservice" in response.data
    assert b"Create New Order" in response.data
    assert b"Active Orders" in response.data


def test_list_orders(client):
    ORDERS = __import__("main").ORDERS
    ORDERS.clear()

    response = client.get("/orders")

    assert response.status_code == 200
    assert response.get_json() == []

def test_dashboard_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"OrderService Microservice" in response.data


def test_list_orders_empty(client):
    from main import ORDERS
    ORDERS.clear()

    response = client.get("/orders")

    assert response.status_code == 200
    assert response.get_json() == []


def test_list_orders_with_data(client):
    client.post("/orders", json={"item": "Laptop", "quantity": 2})

    response = client.get("/orders")

    assert response.status_code == 200
    assert len(response.get_json()) >= 1

def test_create_order_invalid_json(client):
    response = client.post(
        "/orders",
        data="invalid json",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "error" in response.get_json()

