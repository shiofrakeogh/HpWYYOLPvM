from flask import Flask, request, jsonify
from app.query_builder import build_query
import ollama
import json
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

INTENT_PROMPT = """You are a movie query parser. Given a user's question, return JSON with these fields:
{"intent": "lookup|recommend|unknown", "title": "string or null", "genre": "string or null", "year": "int or null", "min_rating": "float or null"}

If the user is asking about a specific movie, classify as "lookup".
If the user is asking for movie suggestions based on criteria, classify as "recommend".
Otherwise classify as "unknown", leave all other fields as null.

Set any fields the user does not mention to null. Do not make up values.
Respond with only a JSON object, no other text.

Example:
User: "tell me about Toy Story"
Output: {"intent": "lookup", "title": "Toy Story", "genre": null, "year": null, "min_rating": null}

User: "recommend some action movies"
Output: {"intent": "recommend", "title": null, "genre": "Action", "year": null, "min_rating": null}
"""

RESPONSE_PROMPT = "You are a movie recommender. Take the query results and give them back to the user in a friendly conversational format."

DATABASE = "movies.db"
MODEL = "llama3"

REQUIRED_KEYS = {"intent", "title", "genre", "year", "min_rating"}


def parse_intent(user_message):
    """Call the LLM to extract structured intent from the user's message."""
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": INTENT_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )
    return json.loads(response["message"]["content"])


def validate_intent(intent):
    """Check that the intent dict has the expected keys and types."""
    if not isinstance(intent, dict):
        return False
    if not REQUIRED_KEYS.issubset(intent.keys()):
        return False
    if intent["intent"] not in ("lookup", "recommend", "unknown"):
        return False
    return True


def execute_query(query, params):
    """Run the SQL query and return results."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


def generate_response(user_message, result):
    """Call the LLM to generate a conversational response from query results."""
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": RESPONSE_PROMPT},
            {"role": "user", "content": f"User asked: {user_message}\nResults: {result}"}
        ]
    )
    return response["message"]["content"]


@app.route("/movies", methods=["POST"])
def movies():
    request_data = request.get_json()
    if not request_data or "message" not in request_data:
        logger.error("No message field in request")
        return jsonify({"error": "message field is required"}), 400

    user_message = request_data["message"]
    logger.info(f"Received message: {user_message}")

    try:
        intent = parse_intent(user_message)
    except json.JSONDecodeError:
        logger.error("LLM returned invalid JSON")
        return jsonify({"error": "server returned malformed response"}), 500

    if not validate_intent(intent):
        logger.error(f"LLM returned invalid intent structure: {intent}")
        return jsonify({"error": "server returned malformed response"}), 500

    if intent["intent"] == "unknown":
        logger.info("Intent classified as unknown")
        return jsonify({"error": "can't help with that specific request"}), 400

    logger.info(f"Parsed intent: {intent}")
    query, params = build_query(intent)

    try:
        result = execute_query(query, params)
        logger.info(f"Query returned {len(result)} results")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "database error"}), 500

    if not result:
        logger.info("No results found")
        return jsonify({"response": "No movies were found matching your criteria."}), 200

    response_text = generate_response(user_message, result)
    logger.info(f"Response generated successfully")
    return jsonify({"response": response_text})


if __name__ == "__main__":
    app.run(debug=True)