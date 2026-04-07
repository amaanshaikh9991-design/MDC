import os
import pandas as pd
import requests
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'movies.csv')
TMDB_API_KEY = "YOUR_TMDB_API_KEY"  # Replace with your TMDB key
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# --- LOAD DATA & ML MODEL ---
def load_data_and_model():
    try:
        df = pd.read_csv(DATA_PATH)
        df = df.fillna('')

        required_cols = ['genre', 'cast', 'director', 'keywords']
        for col in required_cols:
            if col not in df.columns:
                df[col] = ''

        df['tags'] = df['genre'] + ' ' + df['cast'] + ' ' + df['director'] + ' ' + df['keywords']
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['tags'])
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        return df, cosine_sim
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None, None

movies_df, similarity_matrix = load_data_and_model()
title_index = pd.Series(movies_df.index, index=movies_df['title'].str.lower()) if movies_df is not None else None

# --- UTILITY: TMDB Bollywood movies fetch ---
def fetch_bollywood_movies():
    try:
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_original_language=hi&region=IN&sort_by=popularity.desc&page=1"
        response = requests.get(url, timeout=5)
        data = response.json()
        movies = []
        for m in data.get('results', []):
            movies.append({
                "title": m.get('title', 'Unknown'),
                "release_date": m.get('release_date', 'N/A'),
                "rating": m.get('vote_average', 0),
                "poster": TMDB_IMAGE_BASE + m['poster_path'] if m.get('poster_path') else "",
            })
        return movies
    except Exception as e:
        print(f"❌ TMDB fetch error: {e}")
        return []

# --- ROUTES ---
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/home')
def home():
    tmdb_movies = fetch_bollywood_movies()
    if not tmdb_movies and movies_df is not None:
        tmdb_movies = movies_df.head(10).to_dict('records')  # fallback to CSV
    return render_template('index.html', movies=tmdb_movies)

# --- API ENDPOINTS ---
@app.route('/api/movies', methods=['GET'])
def get_movies():
    if movies_df is None:
        return jsonify([])
    data = movies_df[['title', 'genre', 'year', 'rating', 'director']].to_dict('records')
    return jsonify(data)

@app.route('/api/search', methods=['GET'])
def search_movies():
    query = request.args.get('q', '').lower()
    if not query or movies_df is None:
        return jsonify([])
    results = movies_df[movies_df['title'].str.lower().str.contains(query)]
    data = results[['title', 'genre', 'year', 'rating', 'director']].to_dict('records')
    return jsonify(data[:10])

@app.route('/api/recommend', methods=['POST'])
def recommend_movies():
    data = request.json
    title = data.get('title')
    if not title or movies_df is None or similarity_matrix is None:
        return jsonify([])
    idx = title_index.get(title.lower())
    if idx is None:
        return jsonify([])
    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]
    movie_indices = [i[0] for i in sim_scores]
    result = movies_df.iloc[movie_indices][['title', 'genre', 'year', 'rating', 'director']].to_dict('records')
    return jsonify(result)

@app.route('/api/details', methods=['GET'])
def get_details():
    title = request.args.get('title')
    if not title or movies_df is None:
        return jsonify({})
    movie = movies_df[movies_df['title'].str.lower() == title.lower()]
    if movie.empty:
        return jsonify({})
    return jsonify(movie.to_dict('records')[0])

# --- RUN APP ---
if __name__ == '__main__':
    if movies_df is None:
        print("❌ Failed to load movies.csv")
    else:
        print("✅ Server running successfully")
    app.run(debug=True, port=5000)