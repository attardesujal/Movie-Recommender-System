import streamlit as st
import pickle as pk
import pandas as pd
import requests
from pyunpack import Archive
import os

def fetch_poster(movie_id):
    response = requests.get(f'http://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US')
    try:
        data = response.json()
        poster_path = data['poster_path']
        full_path = f'https://image.tmdb.org/t/p/w500/{poster_path}'
        return full_path
    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        return None

def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_movies_posters = []
        for i in movie_list:
            movie_id = movies.iloc[i[0]].movie_id
            poster = fetch_poster(movie_id)
            if poster:
                recommended_movies.append(movies.iloc[i[0]].title)
                recommended_movies_posters.append(poster)
        return recommended_movies, recommended_movies_posters

    except IndexError as e:
        print(f"Movie not found in database: {e}")
        return [], []
    except Exception as e:
        print(f"An error occurred: {e}")
        return [], []

# Decompress the 7z file for similarity matrix
if not os.path.exists('similarity.pkl'):
    Archive('similarity.pkl.7z').extractall('.')

# Load the dictionary from the pickle file
movies_dict = pk.load(open('movies_dict.pkl', 'rb'))
similarity = pk.load(open('similarity.pkl', 'rb'))

# Convert the dictionary to a DataFrame
movies = pd.DataFrame(movies_dict)

# Set the title of the Streamlit app
st.title('Movie Recommender System')

# Create a select box for movie selection
selected_movie_name = st.selectbox(
    'Choose a movie:',
    movies['title'].values)

# Add a button to get recommendations
if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    if names and posters:
        cols = st.columns(len(names))
        for col, name, poster in zip(cols, names, posters):
            with col:
                st.text(name)
                st.image(poster)
    else:
        st.write("No recommendations found.")