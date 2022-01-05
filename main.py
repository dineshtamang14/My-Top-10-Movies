from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

MOVIE_DB_API_KEY = "35c408cf1163143eb09a109502575306"
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(255), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(255))
    img_url = db.Column(db.String(255), nullable=False)


db.create_all()


def add_new_movie(title, img_url, year, description):
    new_movie = Movie(
        title=title,
        year=year,
        description=description,
        rating=None,
        ranking=None,
        review=None,
        img_url=img_url
    )
    db.session.add(new_movie)
    db.session.commit()


class Movie_edit(FlaskForm):
    rating = StringField("Your Rating Out of 10 eg 7.5", validators=[DataRequired()])
    review = StringField("Your Review")
    submit = SubmitField("Done")


class Add_movie(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/")
def home():
    if request.args.get("movie_id"):
        movie_id = request.args.get("movie_id")
        delete_movie = Movie.query.get(movie_id)
        db.session.delete(delete_movie)
        db.session.commit()
        return redirect(url_for("home"))
    movies = db.session.query(Movie).all()
    return render_template("index.html", movies=movies)


@app.route("/update", methods=["POST", "GET"])
def update():
    form = Movie_edit()
    movie_id = request.args.get("movie_id")
    if request.method == "GET":
        movie = Movie.query.get(movie_id)
        return render_template("edit.html", movie=movie, form=form)
    elif request.method == "POST":
        if form.validate_on_submit():
            update_movie = Movie.query.get(movie_id)
            update_movie.rating = form.rating.data
            update_movie.review = form.review.data
            db.session.commit()
        return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = Add_movie()
    if request.method == "GET":
        return render_template("add.html", form=form)
    elif request.method == "POST":
        if form.validate_on_submit():
            search_movies = form.title.data
            response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_DB_API_KEY,
                                                                 "query": search_movies}).json()['results']
            print(response)
            return render_template("select.html", movies=response)


@app.route("/new_movie")
def add_new():
    movie_id = request.args.get("id")
    if movie_id:
        response = requests.get(f"{MOVIE_DB_INFO_URL}/{movie_id}", params={"api_key": MOVIE_DB_API_KEY}).json()
        print(response)
        title = response["original_title"]
        img_url = f"{MOVIE_DB_IMAGE_URL}/{response['poster_path']}"
        year = response["release_date"]
        description = response["overview"]
        add_new_movie(title, img_url, year, description)
    return redirect(url_for('add_movie'))


if __name__ == '__main__':
    app.run(debug=True)
