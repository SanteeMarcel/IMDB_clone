from fastapi import Depends, FastAPI, HTTPException, Response, Request
from starlette.status import HTTP_204_NO_CONTENT, HTTP_202_ACCEPTED, HTTP_201_CREATED, HTTP_200_OK
from sqlalchemy.orm import Session
from . import db_queries, models, schemas
from .database import SessionLocal, engine
from logging.config import dictConfig
import logging
from .log_config import logging_schema_api

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


dictConfig(logging_schema_api)
logger = logging.getLogger("api_logger")


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    db_queries.populate_genres(db)
    db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        logger.error("Could not connect to database", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Internal Server Error - Could not connect to database")
    finally:
        db.close()


@app.post("/api/v1/movies/", status_code=HTTP_202_ACCEPTED, response_model=schemas.Movie)
async def create_movie(movie: schemas.MovieBase, response: Response, request: Request, db: Session = Depends(get_db)):
    logger.info(
        f"{request.method} {request.url} {request.headers} {await request.json()}")
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
async def update_movie(movie_id: int, movie: schemas.MovieBase, response: Response, request: Request, db: Session = Depends(get_db)):
    logger.info(
        f"{request.method} {request.url} {request.headers} {await request.json()}")
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
async def partial_update_movie(movie_id: int, response: Response, request: Request, title: str | None = None, rating: float | None = None, year: int | None = None, genre_id: int | None = None, db: Session = Depends(get_db)):
    logger.info(
        f"{request.method} {request.url} {request.headers} {await request.json()}")
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
async def delete_movie(movie_id: int, response: Response, request: Request, db: Session = Depends(get_db)):
    logger.info(
        f"{request.method} {request.url} {request.headers} {await request.json()}")
    db_movie = db_queries.get_movie_by_id(db, movie_id)
    if not db_movie:
        raise HTTPException(
            status_code=404, detail=f"Missing movie with id {movie_id}")
    response.status_code = HTTP_200_OK
    return db_queries.delete_movie(db=db, movie_id=movie_id)


@app.get("/api/v1/movies/", status_code=HTTP_200_OK, response_model=list[schemas.Movie])
def query_movies(response: Response, request: Request, q: str | None = None, limit: int | None = None, db: Session = Depends(get_db)):
    logger.info(
        f"{request.method} {request.url} {request.headers}")
    if q:
        db_movies = db_queries.get_movies_by_query(db=db, q=q, limit=limit)
        if not db_movies:
            raise HTTPException(status_code=404, detail="No movie was found")
        response.status_code = HTTP_200_OK
        return db_movies
    db_movies = db_queries.get_movies(db=db, limit=limit)
    response.status_code = HTTP_200_OK if len(
        db_movies) > 0 else HTTP_204_NO_CONTENT
    return db_movies


@app.get("/api/v1/movies/{movie_id}", status_code=HTTP_202_ACCEPTED, response_model=schemas.Movie)
def get_movie_by_id(movie_id: int, response: Response, request: Request, db: Session = Depends(get_db)):
    logger.info(
        f"{request.method} {request.url} {request.headers}")
    db_movie = db_queries.get_movie_by_id(db=db, movie_id=movie_id)
    if not db_movie:
        raise HTTPException(
            status_code=404, detail=f"Missing movie with id {movie_id}")
    response.status_code = HTTP_200_OK
    return db_movie


@app.get("/api/v1/genres", status_code=HTTP_202_ACCEPTED, response_model=list[schemas.Genre])
def get_genres(response: Response, request: Request, db: Session = Depends(get_db)):
    logger.info(
        f"{request.method} {request.url} {request.headers}")
    db_genres = db_queries.get_genres(db=db)
    response.status_code = HTTP_200_OK if len(
        db_genres) > 0 else HTTP_204_NO_CONTENT
    return db_genres
