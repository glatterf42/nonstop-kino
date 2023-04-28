from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles

from core.database import Base, SessionLocal, engine
from core.models import MovieShowing

Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static", follow_symlink=True), name="static")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def render_todays_movies(request: Request, db: Session = Depends(get_db)):
    query = select(MovieShowing)
    showings = db.scalars(query).all()
    return templates.TemplateResponse(
        "todays_movies.html", {"request": request, "showings": showings}
    )
