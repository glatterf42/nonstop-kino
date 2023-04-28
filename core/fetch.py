from core.database import SessionLocal
from core.movie_showings import Admiralkino

session = SessionLocal()

for CinemaClass in [Admiralkino]:
    cinema = CinemaClass()
    print(cinema.name)
    for movie in cinema.get_todays_movies():
        session.add(movie)

        print(movie.title)
session.commit()
session.flush()
