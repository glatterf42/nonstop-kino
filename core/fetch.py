from core.database import SessionLocal
from core.models import MovieShowing
from core.movie_showings import Admiralkino

session = SessionLocal()

session.query(MovieShowing).delete()  # delete everything in the table

for CinemaClass in [Admiralkino]:
    cinema = CinemaClass()
    print(cinema.name)
    for movie in cinema.get_todays_movies():
        session.add(movie)

        print(movie.title)
session.commit()
session.flush()
