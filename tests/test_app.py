from app.main import app, validate_intent

def test_missing_message():
    client = app.test_client()
    response = client.post("/movies", json={})
    assert response.status_code == 400

def test_empty_body_returns_400():
    client = app.test_client()
    response = client.post("/movies", content_type="application/json", data="not json")
    assert response.status_code == 400

def test_validate_intent_missing_keys():
    bad_intent = {"intent": "lookup", "title": "Inception"}
    assert validate_intent(bad_intent) == False

def test_validate_intent_valid():
    good_intent = {"intent": "lookup", "title": "Inception", "genre": None, "year": None, "min_rating": None}
    assert validate_intent(good_intent) == True