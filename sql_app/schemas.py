from pydantic import BaseModel


class MovieBase(BaseModel):
    title: str
    rating: float | None = None
    year: int
    genre_id: int


class Movie(MovieBase):
    id: int

    class Config:
        orm_mode = True


class GenreBase(BaseModel):
    name: str


class Genre(GenreBase):
    id: int

    class Config:
        orm_mode = True
