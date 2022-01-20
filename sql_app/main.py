from fastapi import Depends, FastAPI, HTTPException, Response, Request
from starlette.status import HTTP_204_NO_CONTENT, HTTP_202_ACCEPTED, HTTP_201_CREATED, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from sqlalchemy.orm import Session
from . import db_queries, models, schemas
from .database import SessionLocal, engine
from logging.config import dictConfig
import logging
from .log_config import logging_schema_api
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

import uvicorn

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


models.Base.metadata.create_all(bind=engine)
dictConfig(logging_schema_api)
logger = logging.getLogger("api_logger")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


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


@app.get("/api/v1/genres/", status_code=HTTP_202_ACCEPTED, response_model=list[schemas.Genre])
def get_genres(response: Response, request: Request, db: Session = Depends(get_db)):
    logger.info(
        f"{request.method} {request.url} {request.headers}")
    db_genres = db_queries.get_genres(db=db)
    response.status_code = HTTP_200_OK if len(
        db_genres) > 0 else HTTP_204_NO_CONTENT
    return db_genres


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return schemas.UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/api/v1/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestFormStrict = Depends()):
    user = authenticate_user(
        fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/v1/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


SECRET_KEY = "748e5f50fbd00e5dc7ae583e7a5bf27d001f43a17970f6c9796d67b3294da59b"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "John Doe",
        "email": "admin@admin.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "is_active": True,
    }
}


@app.delete("/api/v1/movies/{movie_id}", status_code=HTTP_202_ACCEPTED, response_model=schemas.Movie)
async def delete_movie(movie_id: int, response: Response, request: Request, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    logger.info(
        f"{request.method} {request.url} {request.headers}")
    db_movie = db_queries.get_movie_by_id(db, movie_id)
    if not db_movie:
        raise HTTPException(
            status_code=404, detail=f"Missing movie with id {movie_id}")
    response.status_code = HTTP_200_OK
    return db_queries.delete_movie(db=db, movie_id=movie_id)
