# Movie Query API LLM
A conversational REST API that answers natural language questions about movies using structured data retrieval and LLM powered responses.
## Setup

### Prerequisites
- Python 3.11+
- Ollama with llama3 model installed (`ollama pull llama3`)

### Install Steps

Install the required packages:
```bash
pip install -r requirements.txt
```

Run the data ingestion script to set up the movies database:
```bash
python scripts/ingest.py
```

Ensure Ollama is running:
```bash
ollama serve
```

Start the server:
```bash
python -m app.main
```

## Usage

Leave the server terminal open and open a second terminal to make requests.

**Linux/Mac:**
```bash
curl -X POST http://127.0.0.1:5000/movies -H "Content-Type: application/json" -d '{"message": "tell me about Toy Story"}'
```

**Windows (PowerShell):**
```powershell
$r = Invoke-RestMethod -Uri "http://127.0.0.1:5000/movies" -Method POST -ContentType "application/json" -Body '{"message": "tell me about Toy Story"}'
$r.response
```

**Sample response:**
```
I've got the scoop on Toy Story for you!

You asked about Toy Story, and I'm excited to share some fun facts! Here's what I found:

* Toy Story is an adventure film that was released in 1995.
* It's also an animated movie, perfect for kids of all ages!
* This classic film has been loved by many, with a rating of 3.92 out of 5 stars based on 215 reviews.

You know what's even better? The sequels! Toy Story 2 is another adventure film, released in 1999,
with a rating of 3.86 out of 5 stars based on 97 reviews.
Toy Story 3 is the latest installment, released in 2010, with a rating of 4.11 out of 5 stars
based on 55 reviews.
```

## Approach

This app combines structured data retrieval with LLM powered response.

1. **Intent Parsing:** The user's natural language question is sent to a local LLM (Ollama/llama3) which extracts the intent (lookup/recommend) and returns a JSON object.
    ```json
    {"intent": "lookup", "title": "Toy Story", "genre": null, "year": null, "min_rating": null}
    ```

2. **Query Building:** A parameterised SQL query is dynamically built from the non-null fields in the intent object. This is executed against a SQLite database to retrieve movie data.

3. **Response Generation:** The query results and original question are passed to a second LLM call which generates a conversational answer using the database results.

## API Endpoint

**POST /movies**

Request:
```json
{"message": "your natural language question about movies"}
```

Response (200):
```json
{"response": "conversational answer based on database results"}
```

Error responses:
- `400`: `{"error": "message field is required"}` -> missing or invalid body
- `400`: `{"error": "can't help with that specific request"}` -> unrecognised intent
- `500`: `{"error": "server returned malformed code"}` -> LLM returned invalid JSON
- `500`: `{"error": "database error"}` -> SQL execution failed

## Tests

Run the tests using:
```bash
python -m pytest -v
```

## Known Limitations

- The dataset used (MovieLens) doesn't include overview, cast or director fields. This could be addressed by using the TMDB dataset instead and updating the prompt and SQL query to include these fields.

- Titles stored as, for example, "Matrix, The" instead of "The Matrix" affects title matching. This could be fixed by normalising titles during ingestion (moving "The" back to the front) or stripping "The" before querying.

- LLM responses are non-deterministic, a few tests returned responses with made up values or unexpected types (e.g. lists instead of strings). This could be mitigated with examples in the prompt, but not fully eliminated.

- There is a limit of 10 on queries. A broad recommend query could still return less relevant results. This could be improved with better ranking or relevance scoring (e.g only include movies above a certain rating even if the user hasn't specified). 

- No conversation history, the user can't continue the conversation (e.g. "tell me more about Toy Story"). This could be addressed by using Ollama's `assistant` role to maintain previous replies across requests.