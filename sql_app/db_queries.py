from sqlalchemy.orm import Session
from . import models, schemas


def create_movie(db: Session, movie: schemas.MovieBase):
    db_movie = models.Movie(
        title=movie.title,
        rating=movie.rating,
        year=movie.year,
        genre_id=movie.genre_id
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def update_movie_complete(db: Session, movie_id: int, movie: schemas.MovieBase):
    db_movie = db.query(models.Movie).filter(
        models.Movie.id == movie_id, models.Movie.is_active).first()
    if db_movie:
        db_movie.title = movie.title
        db_movie.rating = movie.rating
        db_movie.year = movie.year
        db_movie.genre_id = movie.genre_id
        db.commit()
        db.refresh(db_movie)
        return db_movie
    return None


def update_movie_partial(db: Session, movie_id: int, movie: schemas.MovieBase):
    db_movie = db.query(models.Movie).filter(
        models.Movie.id == movie_id, models.Movie.is_active).first()
    if db_movie:
        if movie.title:
            db_movie.title = movie.title
        if movie.rating:
            db_movie.rating = movie.rating
        if movie.year:
            db_movie.year = movie.year
        if movie.genre_id:
            db_movie.genre_id = movie.genre_id
        db.commit()
        db.refresh(db_movie)
        return db_movie
    return None


def delete_movie(db: Session, movie_id: int):
    db_movie = db.query(models.Movie).filter(
        models.Movie.id == movie_id, models.Movie.is_active).first()
    if db_movie:
        db_movie.is_active = False
        db.commit()
        db.refresh(db_movie)
        return db_movie
    return None


def get_movie_by_id(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id, models.Movie.is_active).first()


def get_movies(db: Session, limit: int = 100):
    return db.query(models.Movie).filter(models.Movie.is_active).limit(limit).all()


def get_movies_by_query(db: Session, q: str, limit: int = 100):
    return db.query(models.Movie).filter(models.Movie.title.ilike(f"%{q}%"), models.Movie.is_active).limit(limit).all()


def populate_genres(db: Session):
    if not db.query(models.Genre).count():
        db.add_all([
            models.Genre(name='Action'),
            models.Genre(name='Adventure'),
            models.Genre(name='Animation'),
            models.Genre(name='Comedy'),
            models.Genre(name='Crime'),
            models.Genre(name='Documentary'),
            models.Genre(name='Drama'),
            models.Genre(name='Family'),
            models.Genre(name='Fantasy'),
            models.Genre(name='History'),
            models.Genre(name='Horror'),
            models.Genre(name='Music'),
            models.Genre(name='Mystery'),
            models.Genre(name='Romance'),
            models.Genre(name='Science Fiction'),
            models.Genre(name='TV Movie'),
            models.Genre(name='Thriller'),
            models.Genre(name='War'),
            models.Genre(name='Western')
        ])
        db.commit()


def get_genres(db: Session):
    return db.query(models.Genre).filter(models.Genre.is_active).all()
