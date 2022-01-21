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
Delete movie from database(logical delete)

Get - Read
Accessing the pure url "/movies/" get all movies from db, optionally you can have the parameters "?q=" for quering and "?limit=" for limiting the amount of results.

There's another endpoint for getting genres.

# Implementações que eu faria se tivesse mais tempo

Um filme poderia ter múltiplos gêneros e também dá pra aprimorar o end-point para buscar todos os filmes de cada gênero.

Associar uma imagem de cartaz a cada filme, para poder ser exibido com mais facilidade no front-end.

Adicionaria REDIS para cache, assim diminuindo a quantidade de requisições diretas no banco, que faria bastante diferença em alta escala. O REDIS ainda poderia ser utilizado como message broker num sistema de arquitetura de micro-serviços no futuro.

Um filme poderia ter múltiplos gêneros e também dá pra aprimorar o end-point para buscar todos os filmes de cada gênero.

Integrate unit testing to the deployment workflow

Think about more validations on the input.
