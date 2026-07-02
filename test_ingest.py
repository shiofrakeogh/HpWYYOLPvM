import sqlite3

def test_movies_count():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM movies")
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 9742

def test_year_strip():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT year FROM movies WHERE title = ?", ("Toy Story",))
    year = cursor.fetchone()[0]
    conn.close()
    assert year == 1995

def test_genre_count():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM genres")
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 20