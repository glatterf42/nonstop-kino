import re
from dataclasses import dataclass
from datetime import datetime
from typing import Generator

import pytz
import requests
from bs4 import BeautifulSoup

local_tz = pytz.timezone("Europe/Vienna")


@dataclass
class MovieShowing:
    title: str
    time: datetime
    cast: str | None = None
    summary: str | None = None
    genre: str | None = None
    language: str | None = None


class Cinema:
    url: str
    name: str

    def get_html(self):
        r = requests.get(self.url)
        return BeautifulSoup(r.text, "lxml")

    def get_todays_movies(self):
        pass


class Admiralkino(Cinema):
    url = "https://www.admiralkino.at/"
    name = "Admiralkino"

    def get_data(self):
        r = requests.post(
            "https://www.admiralkino.at/wp/wp-admin/admin-ajax.php",
            params={"action": "get_ajax_posts"},
        )
        return r.json()

    def get_todays_movies(self):
        for movie_data in self.get_data():
            showtime = datetime.utcfromtimestamp(movie_data["datetime"])
            showtime = local_tz.localize(showtime)
            if showtime.date() != datetime.today().date():
                continue
            showing = MovieShowing(
                movie_data["title"].title(),
                showtime,
                genre=movie_data["categories"],
                language=movie_data["language"],
            )
            yield showing


class Burgkino(Cinema):
    url = "https://www.burgkino.at/showtimes/today"
    name = "Burgkino"

    def get_todays_movies(self):
        for moviebox in self.get_html().find_all(class_="movies"):
            title = moviebox.find(class_="field--name-node-title").get_text().strip()

            datetime_string = (
                moviebox.find("time").attrs["datetime"].replace("Z", "+00:00")
            )
            showtime = datetime.fromisoformat(datetime_string).astimezone(local_tz)

            try:
                cast = (
                    moviebox.find(class_="field--name-field-cast-teaser")
                    .find(class_="field--item")
                    .get_text()
                    .strip()
                )
            except AttributeError:
                cast = None

            summary = (
                moviebox.find(class_="field--type-text-with-summary")
                .find(class_="field--item")
                .get_text()
                .strip()
            )
            showing = MovieShowing(title, showtime, cast, summary)
            yield showing


class DeFrance(Cinema):
    url = "https://www.votivkino.at/#Programm"
    name = "De France"

    def get_todays_movies(self):
        for film_card in self.get_html().select("li.card.filter_kino_defrance"):
            title = film_card.find(class_="title-heading").get_text()

            datetime_string = (
                film_card.find(class_="showtime_kino_defrance")
                .find(class_="time")
                .attrs["datetime"]
            )
            showdate = datetime.fromisoformat(datetime_string)
            showtime = local_tz.localize(showdate).strftime("%H:%M")

            summary = film_card.find(class_="card-hover-text").get_text()

            # FIXME: this only finds OmU etc, not the exact language
            language = (
                film_card.find(class_="card-hover-duration")
                .find(class_="text")
                .get_text()
                .split("|")
            )[1]
            showing = MovieShowing(title, showtime, summary=summary, language=language)
            yield showing


class Filmcasino(Cinema):
    url = "https://www.filmcasino.at/programm/"
    name = "Filmcasino"

    def get_todays_movies(self):
        for article_wrapper in self.get_html().select("div.article-wrapper.cinema1"):
            # NOTE: many dates may be listed, find finds the first occurrence
            first_date = article_wrapper.find(class_="date").get_text()
            if first_date != datetime.today().strftime("%-d.%-m."):
                continue

            # NOTE: finds only info of first list entry
            times = article_wrapper.find(class_="article-info").find_all(
                class_="disp-time"
            )
            showtimes = [time.get_text().replace("\xa0Uhr", "") for time in times]

            title = article_wrapper.find("h1").get_text()

            for showtime in showtimes:
                showing = MovieShowing(title, showtime)
                yield showing


class Filmhaus(Cinema):
    url = "https://www.filmcasino.at/programm/"
    name = "Filmhaus"

    def get_todays_movies(self):
        for article_wrapper in self.get_html().select("div.article-wrapper.cinema2"):
            # NOTE: many dates may be listed, find finds the first occurrence
            first_date = article_wrapper.find(class_="date").get_text()
            if first_date != datetime.today().strftime("%-d.%-m."):
                continue

            # NOTE: finds only info of first list entry
            times = article_wrapper.find(class_="article-info").find_all(
                class_="disp-time"
            )
            showtimes = [time.get_text().replace("\xa0Uhr", "") for time in times]

            title = article_wrapper.find("h1").get_text()

            for showtime in showtimes:
                showing = MovieShowing(title, showtime)
                yield showing


class Gartenbaukino(Cinema):
    url = "https://www.gartenbaukino.at/programm/programmuebersicht/"
    name = "Gartenbaukino"

    # More elegant way of the following function, I suppose:
    # soup.find_all('script', {'type':'application/ld+json'})
    # data =json.loads(node.contents)
    def get_todays_movies(self):
        for movie_preview in self.get_html().find_all(class_="movie-preview__content"):
            title = movie_preview.find("h2").get_text().strip().title()
            if title == "Geschlossene Veranstaltung":
                continue

            try:
                datetime_string = movie_preview.find("time").attrs["datetime"]
            except AttributeError:
                continue
            showdatetime = datetime.fromisoformat(datetime_string)
            showdate = local_tz.localize(showdatetime).strftime("%Y-%m-%d")
            showtime = local_tz.localize(showdatetime).strftime("%H:%M")

            if showdate != datetime.today().strftime("%Y-%m-%d"):
                continue

            # There is only a description including the director;
            # Not sure we want to include this; available here:
            # description = (
            #     movie_preview.find(class_="movie-preview__description")
            #     .get_text()
            #     .strip()
            # )

            showing = MovieShowing(title, showtime)
            yield showing


class Schikaneder(Cinema):
    url = "https://www.schikaneder.at/kino/kinoprogramm"
    name = "Schikaneder"

    def get_todays_movies(self):
        for entry in (
            self.get_html().find(class_="programm liste").find_all(class_="entry")
        ):
            showdate = entry.find(class_="tag").get_text().split(",")[1].strip()
            if showdate != datetime.today().strftime("%d.%m"):
                continue
            showtime = entry.find(class_="uhrzeit").get_text().strip()

            title = entry.find("h2").get_text().strip().title()
            title = re.sub("\s+", " ", title)

            # Looks like the language is always the last entry here:
            language = entry.find(class_="subinfo").get_text().split(",")[-1].strip()

            summary = entry.find(class_="kurzbeschreibung").get_text()
            summary = re.sub("\s+", " ", summary)

            showing = MovieShowing(title, showtime, summary=summary, language=language)
            yield showing


class Stadtkino(Cinema):
    url = "https://stadtkinowien.at/programm/"
    name = "Stadtkino"

    def get_todays_movies(self):
        for film in self.get_html().find(class_="film-column").find_all(class_="film"):
            # time, _ , language = []
            time = film.find(class_="film-info-box content").get_text()

            title = film.find("h1").get_text()

            language = film.find(class_="film-info-box content small").get_text()

            # NOTE: There is a summary and lots of information, but the summary is
            # incomplete (ends with [...]) and the format not uniform, so we skip
            # this for now
            # summary = film.get_text()

            showing = MovieShowing(title, time, language=language)
            yield showing


class Topkino(Cinema):
    url = "https://www.topkino.at/kino/kinoprogramm"
    name = "Topkino"

    def get_todays_movies(self):
        for entry in (
            self.get_html().find(class_="programm liste").find_all(class_="entry")
        ):
            showdate = entry.find(class_="tag").get_text().split(",")[1].strip()
            if showdate != datetime.today().strftime("%d.%m"):
                continue
            showtime = entry.find(class_="uhrzeit").get_text().strip()

            title = entry.find("h2").get_text().strip().title()
            title = re.sub("\s+", " ", title)

            # Looks like the language is always the last entry here:
            language = entry.find(class_="subinfo").get_text().split(",")[-1].strip()

            summary = entry.find(class_="kurzbeschreibung").get_text()
            summary = re.sub("\s+", " ", summary)

            showing = MovieShowing(title, showtime, summary=summary, language=language)
            yield showing


class Votivkino(Cinema):
    url = "https://www.votivkino.at/#Programm"
    name = "Votivkino"

    def get_todays_movies(self):
        for film_card in self.get_html().select("li.card.filter_kino_votiv"):
            title = film_card.find(class_="title-heading").get_text()

            datetime_string = (
                film_card.find(class_="showtime_kino_votiv")
                .find(class_="time")
                .attrs["datetime"]
            )
            showdate = datetime.fromisoformat(datetime_string)
            showtime = local_tz.localize(showdate).strftime("%H:%M")

            summary = film_card.find(class_="card-hover-text").get_text()

            # FIXME: this only finds OmU etc, not the exact language
            language = (
                film_card.find(class_="card-hover-duration")
                .find(class_="text")
                .get_text()
                .split("|")
            )[1]
            showing = MovieShowing(title, showtime, summary=summary, language=language)
            yield showing


# cinema = Stadtkino()
# cinema.get_todays_movies()

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

cinema_classes = [Stadtkino]

for CinemaClass in cinema_classes:
    cinema = CinemaClass()
    print(cinema.name)
    for movie in cinema.get_todays_movies():
        print(movie.title)
