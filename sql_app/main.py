from fastapi import Depends, FastAPI, HTTPException, Response
from starlette.status import HTTP_202_ACCEPTED, HTTP_201_CREATED, HTTP_200_OK
from sqlalchemy.orm import Session
from . import db_queries, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    db_queries.populate_genres(db)
    db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/v1/movies/", status_code=HTTP_202_ACCEPTED, response_model=schemas.Movie)
def create_movie(movie: schemas.MovieBase, response: Response, db: Session = Depends(get_db)):
    db_movies = db_queries.get_movies_by_query(db, q=movie.title)
    # movies can have the same name or the same year, but not both
    for db_movie in db_movies:
        if db_movie and db_movie.year == movie.year:
            raise HTTPException(status_code=409, detail="Movie already added")
    if movie.rating < 0 or movie.rating > 10:
        raise HTTPException(
            status_code=400, detail="Rating must be between 0 and 10")
    response.status_code = HTTP_201_CREATED
    return db_queries.create_movie(db=db, movie=movie)


@app.put("/api/v1/movies/{movie_id}", status_code=HTTP_202_ACCEPTED, response_model=schemas.Movie)
def update_movie(movie_id: int, movie: schemas.MovieBase, response: Response, db: Session = Depends(get_db)):
    db_movie = db_queries.get_movie_by_id(db, movie_id)
    if not db_movie:
        raise HTTPException(
            status_code=404, detail=f"Missing movie with id {movie_id}")
    db_movie.title = movie.title
    if movie.rating < 0 or movie.rating > 10:
        raise HTTPException(
            status_code=400, detail="Rating must be between 0 and 10")
    db_movie.rating = movie.rating
    db_movie.year = movie.year
    db_movie.genre_id = movie.genre_id
    response.status_code = HTTP_200_OK
    return db_queries.update_movie_complete(db=db, movie_id=movie_id, movie=db_movie)


@app.patch("/api/v1/movies/{movie_id}", status_code=HTTP_202_ACCEPTED, response_model=schemas.Movie)
def partial_update_movie(movie_id: int, response: Response, title: str | None = None, rating: float | None = None, year: int | None = None, genre_id: int | None = None, db: Session = Depends(get_db)):
    db_movie = db_queries.get_movie_by_id(db, movie_id)
    if not db_movie:
        raise HTTPException(
            status_code=404, detail=f"Missing movie with id {movie_id}")
    if title:
        db_movie.title = title
    if rating:
        if rating < 0 or rating > 10:
            raise HTTPException(
                status_code=400, detail="Rating must be between 0 and 10")
        db_movie.rating = rating
    if year:
        db_movie.year = year
    if genre_id:
        db_movie.genre_id = genre_id
    response.status_code = HTTP_200_OK
    return db_queries.update_movie_partial(db=db, movie_id=movie_id, movie=db_movie)


@app.delete("/api/v1/movies/{movie_id}", status_code=HTTP_202_ACCEPTED, response_model=schemas.Movie)
def delete_movie(movie_id: int, response: Response, db: Session = Depends(get_db)):
    db_movie = db_queries.get_movie_by_id(db, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail=f"Missing movie with id {movie_id}")
    response.status_code = HTTP_200_OK
    return db_queries.delete_movie(db=db, movie_id=movie_id)


@app.get("/api/v1/movies/", status_code=HTTP_200_OK, response_model=list[schemas.Movie])
def query_movies(response: Response, q: str | None = None, limit: int | None = None, db: Session = Depends(get_db)):
    if q:
        db_movies = db_queries.get_movies_by_query(db=db, q=q, limit=limit)
        if not db_movies:
            raise HTTPException(status_code=404, detail="No movie was found")
        response.status_code = HTTP_200_OK
        return db_movies
    response.status_code = HTTP_200_OK
    return db_queries.get_movies(db=db, limit=limit)


@app.get("/api/v1/movies/{movie_id}", status_code=HTTP_202_ACCEPTED, response_model=schemas.Movie)
def get_movie_by_id(movie_id: int, response: Response, db: Session = Depends(get_db)):
    db_movie = db_queries.get_movie_by_id(db=db, movie_id=movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail=f"Missing movie with id {movie_id}")
    response.status_code = HTTP_200_OK
    return db_movie


@app.get("/api/v1/genres", status_code=HTTP_202_ACCEPTED, response_model=list[schemas.Genre])
def get_genres(response: Response, db: Session = Depends(get_db)):
    response.status_code = HTTP_200_OK
    return db_queries.get_genres(db=db)
