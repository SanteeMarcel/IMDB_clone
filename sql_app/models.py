from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from .database import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(20), index=True)
    rating = Column(Numeric(1, 2), index=True)
    year = Column(Integer, index=True)

    genre_id = Column(Integer, ForeignKey("genres.id"))
    genre = relationship("Genre", back_populates="movies")


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), index=True)

    movies = relationship("Movie", back_populates="genre")
