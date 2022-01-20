from sql_app.main import app, get_db
from sql_app import models
from sql_app.database import Base
import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = sa.create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


@sa.event.listens_for(engine, "connect")
def do_connect(dbapi_connection, connection_record):
    dbapi_connection.isolation_level = None


@sa.event.listens_for(engine, "begin")
def do_begin(conn):
    conn.exec_driver_sql("BEGIN")


@pytest.fixture()
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    nested = connection.begin_nested()

    @sa.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


def test_get_no_movies(client):
    response = client.get("/api/v1/movies/")
    assert response.status_code == 204
    assert response.json() == []


def test_get_movies_list(client, session):
    session.add(models.Genre(name="Action"))
    session.add(models.Movie(title="Movie 1", year=2000, rating=8, genre_id=1))
    session.add(models.Movie(title="Movie 2", year=2001, rating=9, genre_id=1))
    session.commit()
    response = client.get("/api/v1/movies/")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "title": "Movie 1", "year": 2000, "rating": 8, "genre_id": 1},
        {"id": 2, "title": "Movie 2", "year": 2001, "rating": 9, "genre_id": 1},
    ]


def test_should_create_new_movie(client, session):
    session.add(models.Genre(name="Action"))
    session.commit()
    response = client.post(
        "/api/v1/movies/", json={"title": "Movie 1", "year": 2000, "rating": 8, "genre_id": 1})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": "Movie 1",
                               "year": 2000, "rating": 8, "genre_id": 1}


def test_should_not_create_movie(client, session):
    session.add(models.Genre(name="Action"))
    session.commit()
    response = client.post(
        "/api/v1/movies/", json={"title": "Movie 1", "year": 2000, "rating": 8})
    assert response.status_code == 422
    # improve custom response?


def test_should_update_movie_complete(client, session):
    session.add(models.Genre(name="Action"))
    session.add(models.Movie(title="Movie 1", year=2000, rating=8, genre_id=1))
    session.commit()
    response = client.put(
        "/api/v1/movies/1", json={"title": "Movie 2", "year": 2001, "rating": 9, "genre_id": 1})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Movie 2",
                               "year": 2001, "rating": 9, "genre_id": 1}


def test_should_update_movie_partial(client, session):
    session.add(models.Genre(name="Action"))
    session.add(models.Movie(title="Movie 1", year=2000, rating=8, genre_id=1))
    session.commit()
    response = client.patch(
        "/api/v1/movies/1?title=Movie%202&rating=9&year=2001&genre_id=1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Movie 2",
                               "year": 2001, "rating": 9, "genre_id": 1}


def test_should_not_allow_unauthorized_access(client, session):
    session.add(models.Genre(name="Action"))
    session.add(models.Movie(title="Movie 1", year=2000, rating=8, genre_id=1))
    session.commit()
    response = client.delete("/api/v1/movies/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_should_delete_movie(client, session):
    session.add(models.Genre(name="Action"))
    session.add(models.Movie(title="Movie 1", year=2000, rating=8, genre_id=1))
    session.commit()
    token_response = client.post(
        "/api/v1/token", data={"grant_type": "password", "username": "admin", "password": "secret"})
    assert token_response.status_code == 200
    assert token_response.json()["access_token"] is not None
    assert token_response.json()["token_type"] == "bearer"
    response = client.delete(
        "/api/v1/movies/1", headers={"Authorization": f"Bearer {token_response.json()['access_token']}"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Movie 1",
                               "year": 2000, "rating": 8, "genre_id": 1}


def test_should_not_find_movie_to_delete(client, session):
    session.add(models.Genre(name="Action"))
    session.add(models.Movie(title="Movie 1", year=2000, rating=8, genre_id=1))
    session.commit()
    token_response = client.post(
        "/api/v1/token", data={"grant_type": "password", "username": "admin", "password": "secret"})
    assert token_response.status_code == 200
    assert token_response.json()["access_token"] is not None
    assert token_response.json()["token_type"] == "bearer"
    response = client.delete(
        "/api/v1/movies/2", headers={"Authorization": f"Bearer {token_response.json()['access_token']}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Missing movie with id 2"}


def test_should_get_movie_by_id(client, session):
    session.add(models.Genre(name="Action"))
    session.add(models.Movie(title="Movie 1", year=2000, rating=8, genre_id=1))
    session.commit()
    response = client.get("/api/v1/movies/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "Movie 1",
                               "year": 2000, "rating": 8, "genre_id": 1}


def test_should_query_movies(client, session):
    session.add(models.Genre(name="Action"))
    session.add(models.Movie(title="Movie 1", year=2000, rating=8, genre_id=1))
    session.add(models.Movie(title="Movie 2", year=2001, rating=9, genre_id=1))
    session.commit()
    response = client.get("/api/v1/movies/?q=Movie")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "title": "Movie 1", "year": 2000, "rating": 8, "genre_id": 1},
        {"id": 2, "title": "Movie 2", "year": 2001, "rating": 9, "genre_id": 1},
    ]


def test_should_query_and_limit_movies(client, session):
    session.add(models.Genre(name="Action"))
    session.add(models.Movie(title="Movie 1", year=2000, rating=8, genre_id=1))
    session.add(models.Movie(title="Movie 2", year=2001, rating=9, genre_id=1))
    session.commit()
    response = client.get("/api/v1/movies/?q=Movie&limit=1")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "title": "Movie 1", "year": 2000, "rating": 8, "genre_id": 1},
    ]


def test_should_get_all_genres(client, session):
    session.add(models.Genre(name="Action"))
    session.add(models.Genre(name="Comedy"))
    session.commit()
    response = client.get("/api/v1/genres/")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Action"},
        {"id": 2, "name": "Comedy"},
    ]


print("All tests passed")
