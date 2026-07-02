from flask import Flask, request, jsonify
from query_builder import build_query
import ollama, json, sqlite3, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/movies", methods=["POST"])
def movies():
    requestData = request.get_json()
    if not requestData or "message" not in requestData:
        logger.error("No message field in request")
        return jsonify({"error": "message field is required"}), 400
    
    user_message = requestData["message"]
    logger.info(f"Received message: {user_message}")
    prompt = "You are a movie query parser. Given a user's question, return JSON with these fields: {intent: lookup | recommend | unknown, title: string or null, year: int or null, genre: string or null, min_rating: float or null} If the user is asking about a specific movie, classify as 'lookup', and a 'lookup' should return a single movie row. If the user is looking for multiple movie titles, classify as 'recommend', 'recommend' should return multiple movie rows. Otherwise classify as unknown, leave all other fields as null. Set any fields the user doesn't mention to null. Do not make up values. Respond with only a JSON object, no other text."
    
    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ]
    )

    try:
        responseData = json.loads(response["message"]["content"])
        if responseData["intent"] == "unknown":
            logger.error("The intent of the message couldn't be classified")
            return jsonify({"error": "can't help with that specific request"}), 400
        logger.info(f"Received response JSON data from Ollama: {responseData}")
    except json.JSONDecodeError:
        logger.error("The server returned malformed code")
        return jsonify({"error": "server returned malformed code"}), 500
    
    query, params = build_query(responseData)

    try:
        with sqlite3.connect("movies.db") as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            logger.info(f"Database was successfully queried. Returned {len(result)} results")

    except sqlite3.Error as e:
        logger.error("There was an error with querying the database for results")
        return jsonify({"error": "database error"}), 500        

    prompt = "You are a movie recommender. Take the query results and give them back to the user in a friendly conversational format. "
    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"User asked: {user_message} \n Results: {result}"}
        ]
    )

    responseData = response["message"]["content"]

    logger.info(f"Ollama returned the following result to the user {responseData}")
    return jsonify({"response": responseData})

if __name__ == "__main__":
    app.run(debug=True)