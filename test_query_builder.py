from query_builder import build_query

def test_recommend_genre():
    intent = {"intent": "recommend", "title": None, "genre": "Action", "year": None, "min_rating": None}
    query, params = build_query(intent)
    assert "genres.name LIKE ?" in query
    assert "%Action%" in params

def test_lookup_genre():
    intent = {"intent": "lookup", "title": None, "genre": "Action", "year": None, "min_rating": None}
    query, params = build_query(intent)
    assert "genres.name LIKE ?" in query
    assert "%Action%" in params

def test_multiple_fields():
    intent = {"intent": "lookup", "title": "Pulp Fiction", "genre": "Crime", "year": "1994", "min_rating": 3.0}
    query, params = build_query(intent)
    assert query.count("AND") == 3
    assert len(params) == 4

def test_partial_match():
    intent = {"intent": "lookup", "title": "Pulp fic", "genre": None, "year": None, "min_rating": None}
    query, params = build_query(intent)
    assert "movies.title LIKE ?" in query
    assert "%Pulp fic%" in params