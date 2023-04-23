from flask import Flask, render_template

from movie_showings import *

app = Flask(__name__)

cinema_classes = [
    Admiralkino,
    Burgkino,
    DeFrance,
    Filmcasino,
    Filmhaus,
    Gartenbaukino,
    Schikaneder,
    Stadtkino,
    Topkino,
    Votivkino,
]


@app.route("/")
def hello_world():
    showings = []
    for CinemaClass in cinema_classes:
        cinema = CinemaClass()
        for movie in cinema.get_todays_movies():
            showings.append(movie)

    return render_template("template.html", showings=showings)
