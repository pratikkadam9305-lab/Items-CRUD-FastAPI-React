import json
import logging


import pytest
# 1. Test item creation

def test_create_item(client):
    response = client.post(
        "/api/items",
        json={
            "title": "Laptop",
            "description": "Dell Laptop"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Laptop"
    assert data["description"] == "Dell Laptop"
    assert data["id"] is not None


# 2. Test fetching all items

def test_get_all_items(client):

    client.post(
        "/api/items",
        json={"title": "Laptop"}
    )

    client.post(
        "/api/items",
        json={"title": "Mouse"}
    )

    response = client.get("/api/items")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "Laptop"
    assert data[1]["title"] == "Mouse"


# 3. Test fetching a single item

def test_get_single_item(client):

    create_response = client.post(
        "/api/items",
        json={"title": "Keyboard"}
    )

    item_id = create_response.json()["id"]

    response = client.get(
        f"/api/items/{item_id}"
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Keyboard"


# 4. Test updating an item

def test_update_item(client):

    create_response = client.post(
        "/api/items",
        json={"title": "Old Laptop"}
    )

    item_id = create_response.json()["id"]

    response = client.put(
        f"/api/items/{item_id}",
        json={
            "title": "New Laptop",
            "description": "Updated description"
        }
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New Laptop"
    assert response.json()["description"] == "Updated description"


# 5. Test deleting an item

def test_delete_item(client):

    create_response = client.post(
        "/api/items",
        json={"title": "Tablet"}
    )

    item_id = create_response.json()["id"]

    response = client.delete(
        f"/api/items/{item_id}"
    )

    assert response.status_code == 204

    # Verify that the item no longer exists
    get_response = client.get(
        f"/api/items/{item_id}"
    )

    assert get_response.status_code == 404


# 6. Test invalid input

def test_create_item_invalid_input(client):

    response = client.post(
        "/api/items",
        json={
            "title": "",
            "description": "Invalid item"
        }
    )

    assert response.status_code == 422


# 7. Test fetching a non-existent item

def test_get_nonexistent_item(client):

    response = client.get("/api/items/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


# 8. Test invalid query parameters

@pytest.mark.parametrize(
    "params",
    [
        {"skip": -1},
        {"limit": 0},
        {"limit": 101},
        {"sort_by": "price"},
        {"sort_order": "random"},
    ]
)
def test_invalid_query_parameters(client, params):

    response = client.get("/api/items", params=params)

    assert response.status_code == 422


# 9. Test valid query parameters

@pytest.mark.parametrize(
    "params",
    [
        {"skip": 0},
        {"skip": 10},
        {"limit": 1},
        {"limit": 100},
        {"sort_by": "title"},
        {"sort_by": "created_at"},
        {"sort_order": "asc"},
        {"sort_order": "desc"},
    ]
)
def test_valid_query_parameters(client, params):

    response = client.get("/api/items", params=params)

    assert response.status_code == 200



# 10. Test successful API request logging

def test_successful_request_logging(client, caplog):

    with caplog.at_level(logging.INFO, logger="api.request"):
        response = client.get("/api/items")

    assert response.status_code == 200

    records = [
        record for record in caplog.records
        if record.name == "api.request"
    ]

    assert records

    log_data = json.loads(records[-1].message)

    assert log_data["method"] == "GET"
    assert log_data["path"] == "/api/items"
    assert log_data["status_code"] == 200
    assert log_data["processing_time_ms"] >= 0
    assert "timestamp" in log_data


# 11. Test failed API request logging

def test_failed_request_logging(client, caplog):

    with caplog.at_level(logging.INFO, logger="api.request"):
        response = client.get("/api/items/9999")

    assert response.status_code == 404

    records = [
        record for record in caplog.records
        if record.name == "api.request"
    ]

    assert records

    log_data = json.loads(records[-1].message)

    assert log_data["method"] == "GET"
    assert log_data["path"] == "/api/items/9999"
    assert log_data["status_code"] == 404


# 12. Test sensitive query parameters are not logged

def test_sensitive_data_not_logged(client, caplog):

    with caplog.at_level(logging.INFO, logger="api.request"):
        client.get("/api/items?token=secret123")

    records = [
        record for record in caplog.records
        if record.name == "api.request"
    ]

    assert records

    for record in records:
        assert "secret123" not in record.message

        log_data = json.loads(record.message)

        assert log_data["path"] == "/api/items"
        assert "token" not in log_data

def test_health(client):

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}