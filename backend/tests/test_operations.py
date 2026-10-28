from tests.test_store_settings import client, db_session


def test_readiness_checks_database_and_returns_a_request_reference(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
    assert len(response.headers["X-Request-ID"]) == 32


def test_readiness_failure_does_not_expose_database_errors(client, db_session, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("private connection details")
    monkeypatch.setattr(db_session, "execute", fail)
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable."}
    assert "private" not in response.text
    assert client.get("/health").status_code == 200
