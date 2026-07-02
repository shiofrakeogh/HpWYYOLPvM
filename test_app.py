from main import app

def test_missing_message():
    client = app.test_client()
    response = client.post("/movies", json={})
    assert response.status_code == 400