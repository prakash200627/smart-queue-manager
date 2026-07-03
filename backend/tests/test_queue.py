def test_counter_auth_protection(client):
    # No token -> 401
    res = client.post("/counter/add", json={"name": "C1", "service_type": "Passport"})
    assert res.status_code == 401
    assert "Unauthorized" in res.json["error"]

def test_counter_role_restriction(client, operator_headers):
    # Operator is not Admin -> 403
    res = client.post("/counter/add", json={"name": "C1", "service_type": "Passport"}, headers=operator_headers)
    assert res.status_code == 403
    assert "Forbidden" in res.json["error"]

def test_counter_add_and_delete_happy_path(client, admin_headers):
    # Add counter
    res = client.post("/counter/add", json={"name": "Counter 1", "service_type": "Passport"}, headers=admin_headers)
    assert res.status_code == 200
    assert "Counter created successfully" in res.json["message"]

    # Verify added
    res = client.get("/counter/all")
    assert res.status_code == 200
    counters = res.json
    assert len(counters) == 1
    assert counters[0]["name"] == "Counter 1"
    counter_id = counters[0]["id"]

    # Delete counter
    res = client.delete(f"/counter/delete/{counter_id}", headers=admin_headers)
    assert res.status_code == 200
    assert "Counter deleted" in res.json["message"]

    # Verify deleted
    res = client.get("/counter/all")
    assert len(res.json) == 0

def test_counter_add_validation_invalid_service_type(client, admin_headers):
    res = client.post("/counter/add", json={"name": "C1", "service_type": "InvalidService"}, headers=admin_headers)
    assert res.status_code == 400
    assert res.json["field"] == "service_type"

def test_queue_flow_happy_path(client, admin_headers):
    # Create Counter
    client.post("/counter/add", json={"name": "Passport Counter", "service_type": "Passport"}, headers=admin_headers)
    
    # Get Counter ID
    counters_res = client.get("/counter/all")
    counter_id = counters_res.json[0]["id"]

    # Create Token
    res = client.post("/queue/new", json={"service_type": "Passport"})
    assert res.status_code == 200
    assert "token" in res.json
    token_number = res.json["token"]
    assert res.json["counter"] == "Passport Counter"

    # Get Next Token
    res = client.get(f"/queue/counter/{counter_id}/next")
    assert res.status_code == 200
    assert res.json["token_number"] == token_number
    assert res.json["is_serving"] is False
    token_id = res.json["token_id"]

    # Get Waiting Tokens
    res = client.get(f"/queue/counter/{counter_id}/tokens")
    assert res.status_code == 200
    assert len(res.json) == 1
    assert res.json[0]["token_number"] == token_number

    # Start Service
    res = client.post(f"/queue/start/{token_id}")
    assert res.status_code == 200
    assert "Service started" in res.json["message"]

    # Finish Service
    res = client.post(f"/queue/finish/{token_id}")
    assert res.status_code == 200
    assert "Service completed" in res.json["message"]

def test_queue_ai_detect_happy_path(client):
    res = client.post("/queue/ai-detect", json={"message": "I want to renew my driving license"})
    assert res.status_code == 200
    assert res.json["service"] == "License"

def test_start_service_token_not_found(client):
    res = client.post("/queue/start/999")
    assert res.status_code == 404
    assert "Token not found" in res.json["error"]
