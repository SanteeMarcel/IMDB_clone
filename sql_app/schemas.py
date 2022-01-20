from tkinter.messagebox import NO
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


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    is_active: bool | None = True


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
