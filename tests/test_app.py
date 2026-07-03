from app.main import app

def test_missing_message():
    client = app.test_client()
    response = client.post("/movies", json={})
    assert response.status_code == 400

def test_empty_body_returns_400():
    client = app.test_client()
    response = client.post("/movies", content_type="application/json", data="not json")
    assert response.status_code == 400