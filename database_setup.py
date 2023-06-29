import sqlite3
import pandas as pd

conn = sqlite3.connect('movies.db')

# Create the movies and ratings table
conn.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        tconst TEXT PRIMARY KEY,
        primaryTitle TEXT,
        runtimeMinutes INTEGER,
        genres TEXT,
        numVotes INTEGER
    )
''')

conn.execute('''
    CREATE TABLE IF NOT EXISTS ratings (
        tconst TEXT PRIMARY KEY,
        averageRating REAL,
        numVotes INTEGER
    )
''')

# to read movies and ratings csv files
movies_df = pd.read_csv('movies.csv')
ratings_df = pd.read_csv('ratings.csv')

# Populate the movies and ratings table
movies_df.to_sql('movies', conn, if_exists='replace', index=False)
ratings_df.to_sql('ratings', conn, if_exists='replace', index=False)

conn.close()
