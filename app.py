from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return 'Welcome to the Movie API!'


@app.route('/api/v1/longest-duration-movies')
def get_longest_duration_movies():
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT tconst, primaryTitle, runtimeMinutes, genres
        FROM movies
        ORDER BY runtimeMinutes DESC
        LIMIT 10
    ''')
    movies = [dict(row) for row in cursor]
    conn.close()
    return jsonify(movies)


@app.route('/api/v1/new-movie', methods=['POST'])
def add_new_movie():
    data = request.json
    tconst = data['tconst']
    primary_title = data['primaryTitle']
    runtime_minutes = data['runtimeMinutes']
    genres = data['genres']
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO movies (tconst, primaryTitle, runtimeMinutes, genres)
        VALUES (?, ?, ?, ?)
    ''', (tconst, primary_title, runtime_minutes, genres))
    conn.commit()
    conn.close()
    
    return 'success'

@app.route('/api/v1/top-rated-movies')
def get_top_rated_movies():
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT m.tconst, m.primaryTitle, m.genres, r.averageRating
        FROM movies AS m
        INNER JOIN ratings AS r ON m.tconst = r.tconst
        WHERE r.averageRating > 6.0
        ORDER BY r.averageRating DESC
    ''')
    movies = [dict(row) for row in cursor]
    conn.close()
    return jsonify(movies)

@app.route('/api/v1/genre-movies-with-subtotals')
def get_genre_movies_with_subtotals():
    conn = get_db_connection()
    cursor = conn.execute('''
        SELECT genres, primaryTitle, SUM(r.numVotes) AS numVotes
        FROM movies m
        INNER JOIN ratings r ON m.tconst = r.tconst
        WHERE genres != ''
        GROUP BY genres, primaryTitle
        ORDER BY genres, primaryTitle
    ''')
    rows = cursor.fetchall()
    movies = []
    current_genre = None
    genre_total = 0
    for row in rows:
        genre = row['genres']
        primary_title = row['primaryTitle']
        num_votes = row['numVotes']
        if genre != current_genre:
            if current_genre is not None:
                movies.append({'Genre': 'TOTAL', 'primaryTitle': '', 'numVotes': genre_total})
            current_genre = genre
            genre_total = num_votes
        else:
            genre_total += num_votes
        movies.append({'Genre': genre, 'primaryTitle': primary_title, 'numVotes': num_votes})
    movies.append({'Genre': 'TOTAL', 'primaryTitle': '', 'numVotes': genre_total})
    conn.close()
    return jsonify(movies)


@app.route('/api/v1/update-runtime-minutes', methods=['POST'])
def update_runtime_minutes():
    conn = get_db_connection()
    conn.execute('''
        UPDATE movies
        SET runtimeMinutes = CASE
            WHEN genres = 'Documentary' THEN runtimeMinutes + 15
            WHEN genres = 'Animation' THEN runtimeMinutes + 30
            ELSE runtimeMinutes + 45
        END
    ''')
    conn.commit()
    conn.close()
    return 'success'

if __name__ == '__main__':
    app.run()
