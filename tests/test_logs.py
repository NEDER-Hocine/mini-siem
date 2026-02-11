from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_root_running():
    response = client.get("/")
    assert response.status_code == 200
    assert "Mini SIEM API" in response.json()["message"]


def test_create_and_list_log():
    # create a log
    payload = {
        "source": "firewall",
        "event_type": "login",
        "message": "Failed login attempt",
        "severity": "failed",
    }
    headers = {"X-API-Key": "super-secret-mini-siem-key"}
    resp_create = client.post("/logs/", json=payload, headers=headers)
    assert resp_create.status_code == 200
    created = resp_create.json()
    assert created["source"] == payload["source"]
    assert created["event_type"] == payload["event_type"]

    # list logs
    resp_list = client.get("/logs/")
    assert resp_list.status_code == 200
    logs = resp_list.json()
    assert any(log["id"] == created["id"] for log in logs)

