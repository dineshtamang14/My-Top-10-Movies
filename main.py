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
key = "35c408cf1163143eb09a109502575306"
url = "https://api.themoviedb.org/3/search/"


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(255), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(255), nullable=False)
    img_url = db.Column(db.String(255), nullable=False)


db.create_all()

new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)
# db.session.add(new_movie)
# db.session.commit()


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
            response = requests.get(f"https://api.themoviedb.org/3/movie/"
                                    f"{search_movies}?api_key={key}&language=en-US").json()
            print(response)
            return redirect(url_for('add_movie'))


if __name__ == '__main__':
    app.run(debug=True)
