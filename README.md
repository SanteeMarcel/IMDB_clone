# How to run

In the terminal, change to the project directory

Create and activate a venv. (Optional step, dependent on which OS you are using.

pip install -r requirements.txt

pytest unit_tests\api_tests.py

uvicorn sql_app.main:app --reload

access http://127.0.0.1:8000/docs for the openAPI

Docker alternative:

In the terminal:

docker-compose up

access http://localhost:8000/docs

Cloud alternatives

https://imdbcloneapp1-z5tw3oezda-rj.a.run.app/docs
Old manually deployed version

https://hello-cloud-run-z5tw3oezda-rj.a.run.app/docs
Directly ran from the deploy branch.

# How does it works?

This repository is a simple RESTful API for a movie database, each endpoint is a REST method. The database is relational, with a genre table acting as a foreign key for movie database. The endpoints follow basic CRUD:

Post - Create
Add a movie to the database, do validations

Put - Update
Update all movie data

Patch - Updade
Update movie data partially.

Delete - Delete
Delete movie from database. Logical delete and requires password flow Oauth2 authentication.

Get - Read
Accessing the pure url "/movies/" get all movies from db, optionally you can have the parameters "?q=" for quering and "?limit=" for limiting the amount of results.

There's another endpoint for getting genres. And endpoints implementing Oauth2 authentication.
