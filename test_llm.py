from unittest.mock import patch
from main import app

@patch("main.ollama.chat")
def test_llm_request_response(test_ollama):
    test_ollama.side_effect = [
        {"message": {"content": '{"intent": "lookup", "title": "Inception", "genre": null, "year": null, "min_rating": null}'}},
        {"message": {"content": "Inception is a 2010 sci-fi thriller etc"}}
    ]

    client = app.test_client()
    response = client.post("/movies", json={"message": "Lookup Inception"})
    assert response.status_code == 200
    assert "Inception" in response.get_json()["response"]