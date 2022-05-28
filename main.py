import streamlit as st
import json
from Recommend import KNearestNeighbours
from operator import itemgetter
import pyrebase

firebaseConfig = {
    'apiKey': "AIzaSyAPbPMpXTnI1uTgT3IA7uUcnalw_eoIBj0",
    'authDomain': "movie-recommendation-sys-d73b8.firebaseapp.com",
    'projectId': "movie-recommendation-sys-d73b8",
    'storageBucket': "movie-recommendation-sys-d73b8.appspot.com",
    'messagingSenderId': "156110014293",
    'appId': "1:156110014293:web:c79ac73f3afde1e587d1dc",
    'measurementId': "G-HVCYG4YPH4",
    'databaseURL': "https://movie-recommendation-sys-d73b8-default-rtdb.europe-west1.firebasedatabase.app/"
}

# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Database
db = firebase.database()
storage = firebase.storage()
# Load data and movies list from corresponding JSON files
with open(r'data.json', 'r+', encoding='utf-8') as f:
    data = json.load(f)
with open(r'titles.json', 'r+', encoding='utf-8') as f:
    movie_titles = json.load(f)


def knn(test_point, k):
    # Create dummy target variable for the KNN Classifier
    target = [0 for item in movie_titles]
    # Instantiate object for the Classifier
    model = KNearestNeighbours(data, target, test_point, k=k)
    # Run the algorithm
    model.fit()
    # Distances to most distant movie
    max_dist = sorted(model.distances, key=itemgetter(0))[-1]
    # Print list of 10 recommendations < Change value of k for a different number >
    table = list()
    for i in model.indices:
        # Returns back movie title and imdb link
        table.append([movie_titles[i][0], movie_titles[i][2]])
    return table

if __name__ == '__main__':
    genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
              'Fantasy', 'Film-Noir', 'Game-Show', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Thriller', 'War', 'Western']

    movies = [title[0] for title in movie_titles]
    # st.header('Movie Recommendation System')
    st.set_page_config(page_title="Movie App", page_icon=":clapper:", layout="wide")
    st.title("CINEMY")

    st.image("backgroundImg.jfif", use_column_width='auto', clamp=bool)
    st.sidebar.title("CINEMY APP")
    choice = st.sidebar.selectbox('Login/Signup', ['Login', 'Sign up'])
    email = st.sidebar.text_input("Please enter your email address", value="")
    password = st.sidebar.text_input('Please enter your password', value="")
    if choice == 'Sign up':
        handle = st.sidebar.text_input('Please input your Username', value='Default')
        submit = st.sidebar.button('Create my account')

        if submit:
            if email and password is not None:
                user = auth.create_user_with_email_and_password(email, password)
                st.success('Your account is created successfully')

                # Sign in
                user1 = auth.sign_in_with_email_and_password(email, password)
                db.child(user['localId']).child("Handle").set(handle)
                db.child(user['localId']).child("ID").set(user['localId'])
                st.title('Welcome' + ' ' + handle)
                st.info('Kindly Login')
            else:
                st.sidebar.error("Enter all fields")
    elif choice == 'Login':
        Username = st.sidebar.text_input('Please enter your Username ', value='Default')
        login = st.sidebar.button('Login')
        if login:
            if email and password is not None:
                user = auth.sign_in_with_email_and_password(email, password)

                db.child(user['localId']).child("Handle").set(Username)
                st.subheader("Hi" + ' ' + Username + "!")

            else:
                st.sidebar.error("Enter all fields")

    apps = ['--Select--', 'Movie based', 'Genres based']
    app_options = st.selectbox('Select application:', apps)

    if app_options == 'Movie based':
        movie_select = st.selectbox('Select movie:', ['--Select--'] + movies)
        if movie_select == '--Select--':
            st.write('Select a movie')
        else:
            n = st.number_input('Number of movies:', min_value=5, max_value=20, step=1)
            st.subheader("Recommended Movies")
            genres = data[movies.index(movie_select)]
            test_point = genres
            table = knn(test_point, n)
            for movie, link in table:
                st.markdown("---")
                with st.container():
                    name_column, button_column = st.columns((1, 2))
                    with name_column:
                        st.write(movie)
                    with button_column:
                        st.write("Follow link to see details")
                        st.markdown(link)

    elif app_options == apps[2]:
        options = st.multiselect('Select genres:', genres)
        if options:
            imdb_score = st.slider('IMDb score:', 1, 10, 8)
            n = st.number_input('Number of movies:', min_value=5, max_value=20, step=1)
            st.subheader("Recommended Movies")
            test_point = [1 if genre in options else 0 for genre in genres]
            test_point.append(imdb_score)
            table = knn(test_point, n)
            for movie, link in table:
                st.markdown("---")
                with st.container():
                    name_column, button_column = st.columns((1, 2))
                    with name_column:
                        st.write(movie)
                    with button_column:
                        st.write("Follow link to see details")
                        st.markdown(link)

        else:
            st.write("This is a simple Movie Recommender application. "
                     "You can select the genres and change the IMDb score.")

st.markdown("---")
st.subheader(":mailbox: Contact Me!")
contact_form = """
 <form action="https://formsubmit.co/bhavnaawasthi987612@gmail.com" method="POST">
     <input type="hidden" name="_captcha" value="false">
     <input type="text" name="name" placeholder="Enter your name" required>
     <input type="email" name="email" placeholder="Enter your email" required>
     <textarea name="message" placeholder="Your message here"></textarea>
     <button type="submit">Send</button>
</form>
 """
st.markdown(contact_form, unsafe_allow_html=True)


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("style/style.css")
