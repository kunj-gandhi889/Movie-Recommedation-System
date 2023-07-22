import streamlit as st
import pickle
import requests
import numpy as np
from PIL import Image
import bz2

API_KEY = "0e5c19174daf532b7223e477ca28201f"
IMAGE_PATH = "https://image.tmdb.org/t/p/w342"

img = Image.open('4221419.png')
st.set_page_config(page_title='Movie Recommedation',page_icon=img,layout="wide")   # it will configure default setting of the page

def convertTime(time):
    hour = time//60
    min = time%60

    return f"{hour} hour(s) {min} min(s)"

def suggestion(movie_name):
    """
        input: name of movie (must be in dataset)
        output: top 10 movies with highest similarity with input movie
    """
    idx = df.query(f'title == "{movie_name}"').index[0]  # idx of movie
    simlarity = sorted(list(enumerate(simlr[idx])),reverse=True,key=lambda x:x[1])  
    
    # extracting top 10 movies
    movie_list = simlarity[1:11]  # first will always be movie itself
    
    names = []
    images = []
    release_date = []
    overview = []
    ratings = []
    genres = []
    tagline = []
    production_companies = []
    cast = []
    director = []
    runtime = []

    for i in movie_list:
        idx = df.loc[i[0]].id
        data = requests.get(f"https://api.themoviedb.org/3/movie/{idx}?api_key={API_KEY}&language=en-us")
        data = data.json()
        metadata = requests.get(f'https://api.themoviedb.org/3/movie/{idx}/credits?api_key={API_KEY}')
        metadata = metadata.json()

        if(data['poster_path'] is not None):
            names.append(data['original_title'])
            PHOTO_PATH = IMAGE_PATH+data['poster_path']
            images.append(PHOTO_PATH)
            release_date.append(data['release_date'])
            overview.append(data['overview'])
            ratings.append(data['vote_average'])
            tagline.append(data['tagline'])
            genres.append(", ".join(j['name'] for j in data['genres']))
            production_companies.append(", ".join(j['name'] for j in data['production_companies']))
            cast.append(", ".join(f"{j['character']} (<b>{j['name']}</b>)" for j in metadata['cast'][:8]))
            director.append(", ".join(j['name'] for j in metadata['crew'] if j['job']=='Director'))
            runtime.append(convertTime(data['runtime']))

    return names,images,release_date,overview,ratings,genres,tagline,production_companies,cast,director,runtime

st.markdown(
    """
    <style>
        .css-z5fcl4{
            padding-top:2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Movie Recommender System')

with bz2.BZ2File('movies.pbz2','rb') as f:
    df = pickle.load(f)

with bz2.BZ2File('comp_cosine.pbz2','rb') as f:
    simlr = pickle.load(f)

movies_db = df['title'].values
movies_db = np.append(['Choose Movie'],movies_db)
movie_name = st.selectbox(
    label="Choose a Movie",
    options=movies_db
)

if movie_name != 'Choose Movie':
    idx = df.query(f'title == "{movie_name}"').id.iloc[0]

    url = f"https://api.themoviedb.org/3/movie/{idx}?api_key={API_KEY}&language=en-us"
    movie_data = requests.get(url)
    movie_data = movie_data.json()

    movie_metadata = requests.get(f'https://api.themoviedb.org/3/movie/{idx}/credits?api_key={API_KEY}')
    movie_metadata = movie_metadata.json()
    col1,col2 = st.columns([3,1],gap='large')

    with col1:
        st.header(f"{movie_data['original_title']} - ({movie_data['vote_average']}/10)")
        st.caption(movie_data['tagline'])
        st.write(movie_data['overview'])
        st.write(f'Production Companies: <b>{", ".join(j["name"] for j in movie_data["production_companies"])}</b>',unsafe_allow_html=True)
        cast = ", ".join(f"{j['character']} (<b>{j['name']}</b>)" for j in movie_metadata["cast"][:8])
        st.write(f'Cast: {cast}',unsafe_allow_html=True)
        crew = ", ".join(j['name'] for j in movie_metadata['crew'] if j['job']=='Director')
        st.write(f'Director: <b>{crew}</b>',unsafe_allow_html=True)
        genre = ", ".join(j['name'] for j in movie_data['genres'])
        st.write(f'Genres: <b>{genre}</b><br>Release Date: <b>{movie_data["release_date"]}</b>',unsafe_allow_html=True)
        st.write(f'Runtime: <b>{convertTime(movie_data["runtime"])}</b>',unsafe_allow_html=True)
    with col2:
        st.image(IMAGE_PATH+movie_data['poster_path'])

    if st.button('Recommend Movies'):
        names,images,release_date,overview,ratings,genres,tagline,production_comp,cast,crew,runtime = suggestion(movie_name)

        for i in range(len(names)):

            st.divider()
            col1,col2 = st.columns([3,1],gap='large')
            with col1:
                st.header(f'{names[i]} - ({ratings[i]}/10)')
                st.caption(tagline[i])
                st.write(f'{overview[i]}')
                st.write(f'Production Companies: <b>{production_comp[i]}</b>',unsafe_allow_html=True)
                st.write(f'Cast: {cast[i]}',unsafe_allow_html=True)
                st.write(f'Director: <b>{crew[i]}</b>',unsafe_allow_html=True)
                st.write(f'Genres: <b>{genres[i]}</b><br>Release Date: <b>{release_date[i]}</b>',unsafe_allow_html=True)
                st.write(f'Runtime: <b>{runtime[i]}</b>',unsafe_allow_html=True)
            with col2:
                st.image(images[i])