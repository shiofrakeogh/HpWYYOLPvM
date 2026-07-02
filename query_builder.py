import sqlite3

def build_query(intent):
    base_query = "SELECT title, year, name, avg_rating, rating_count FROM movies INNER JOIN movie_genres ON movies.movie_id = movie_genres.movie_id INNER JOIN genres ON genres.genre_id = movie_genres.genre_id LEFT JOIN ratings ON movies.movie_id = ratings.movie_id"
    where = []
    params = []
    if intent["title"] is not None:
        where.append("movies.title LIKE ?")
        params.append(f"%{intent['title']}%")
    if intent["genre"] is not None:
        where.append("genres.name LIKE ?")
        params.append(f"%{intent['genre']}%")
    if intent["year"] is not None:
        where.append("movies.year = ?")
        params.append(intent["year"])
    if intent["min_rating"] is not None:
        where.append("ratings.avg_rating >= ?")
        params.append(intent["min_rating"])
    if where:
        base_query += " WHERE " + " AND " .join(where)

    return base_query, params
       