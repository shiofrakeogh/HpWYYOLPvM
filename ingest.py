import re
import sqlite3
import csv

database = "movies.db"
create_tables = [

"""DROP TABLE IF EXISTS movie_genres;""",
"""DROP TABLE IF EXISTS ratings;""",
"""DROP TABLE IF EXISTS movies;""",
"""DROP TABLE IF EXISTS genres;""",

"""CREATE TABLE IF NOT EXISTS movies (
    movie_id INT PRIMARY KEY,
    title TEXT NOT NULL,
    year INT
);""",

"""CREATE TABLE IF NOT EXISTS genres (
    genre_id INT PRIMARY KEY,
    name TEXT NOT NULL
);""",

"""CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id INT,
    genre_id INT,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);""",

"""CREATE TABLE IF NOT EXISTS ratings (
    movie_id INT PRIMARY KEY,
    avg_rating FLOAT,
    rating_count INT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);"""
]
try:
    with sqlite3.connect(database) as conn:
        #Create tables in database
        cursor = conn.cursor()
        for statement in create_tables:
            cursor.execute(statement)
        conn.commit()
        print("Tables created successfully.")

        #Ingest movies data into the database
        with open("ml-latest-small/movies.csv", "r", encoding="utf-8") as file:
            movies = csv.reader(file)
            header = next(movies)
            insert_movies = "INSERT INTO movies (movie_id, title, year) VALUES (?, ?, ?)"
            for row in movies:
                #File format: movie_id, title, genres
                movie_id = int(row[0])
                raw_title = row[1].strip()
                raw_genres = row[2].strip()

                #Take out the year from the title
                #Matches 4 digits of the year inside brackets at the end of the text
                match = re.search(r"\((\d{4})\)$", raw_title)

                if match:
                    year = int(match.group(1))
                    #Remove the year from the title
                    title = re.sub(r"\s*\(\d{4}\)$", "", raw_title)
                else:
                    year = None  #Some movies don't have a year in the title
                    title = raw_title

                cursor.execute(insert_movies, (movie_id, title, year))

                #Ingest genres data into the database
                genres = raw_genres.split("|")
                insert_genres = "INSERT OR IGNORE INTO genres (genre_id, name) VALUES (?, ?)"
                insert_movie_genres = "INSERT INTO movie_genres (movie_id, genre_id) VALUES (?, ?)"
                for genre in genres:
                    cursor.execute("SELECT genre_id FROM genres WHERE name = ?", (genre,))
                    result = cursor.fetchone()
                    if result:
                        genre_id = result[0]
                    else:
                        cursor.execute("SELECT MAX(genre_id) FROM genres")
                        max_id = cursor.fetchone()[0]
                        genre_id = (max_id + 1) if max_id is not None else 1
                        cursor.execute(insert_genres, (genre_id, genre))
                    cursor.execute(insert_movie_genres, (movie_id, genre_id))
            conn.commit()

            
            with open("ml-latest-small/ratings.csv", "r", encoding="utf-8") as file:
                ratings = csv.reader(file)
                header = next(ratings)
                insert_ratings = "INSERT INTO ratings (movie_id, avg_rating, rating_count) VALUES (?, ?, ?)"
                ratings_data = {}
                for row in ratings:
                    movie_id = int(row[1])
                    rating = float(row[2])
                    if movie_id not in ratings_data:
                        ratings_data[movie_id] = [0, 0]
                    ratings_data[movie_id][0] += rating
                    ratings_data[movie_id][1] += 1

                for movie_id in ratings_data:
                    cursor.execute(insert_ratings, (movie_id, ratings_data[movie_id][0] / ratings_data[movie_id][1], ratings_data[movie_id][1]))
                conn.commit()
                print("Ratings added.")

                    
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
