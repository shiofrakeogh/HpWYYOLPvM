from flask import Flask, request, jsonify
from query_builder import build_query
import ollama, json, sqlite3

app = Flask(__name__)

@app.route("/movies", methods=["POST"])
def movies():
    requestData = request.get_json()
    user_message = requestData["message"]
    prompt = "You are a movie query parser. Given a user's question, return JSON with these fields: {intent: lookup | recommend | unknown, title: string or null, year: int or null, genre: string or null, min_rating: float or null} If the user is asking about a specific movie, classify as 'lookup', and a 'lookup' should return a single movie row. If the user is looking for multiple movie titles, classify as 'recommend', 'recommend' should return multiple movie rows. Otherwise classify as unknown, leave all other fields as null. Set any fields the user doesn't mention to null. Do not make up values. Respond with only a JSON object, no other text."
    
    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ]
    )

    responseData = json.loads(response["message"]["content"])
    query, params = build_query(responseData)

    try:
        with sqlite3.connect("movies.db") as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    prompt = "You are a movie recommender. Take the query results and give them back to the user in a friendly conversational format. "
    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"User asked: {user_message} \n Results: {result}"}
        ]
    )

    responseData = response["message"]["content"]

    return jsonify({"response": responseData})

if __name__ == "__main__":
    app.run(debug=True)