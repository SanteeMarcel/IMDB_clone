# Como rodar

No terminal do diretorio do projeto:

Crie e ative um venv. (Opcional e dependente do sistema operacional)

pip install -r requirements.txt

pytest unit_tests\api_tests.py

uvicorn sql_app.main:app --reload

acesse http://127.0.0.1:8000/docs para o swagger

Alternativa com Docker:

no terminal digite docker-compose up

acesse http://localhost:8000/docs

Alternativa online:

https://imdbcloneapp1-z5tw3oezda-rj.a.run.app/docs
Versão subida pelo CLI da GCP da main branch

https://hello-cloud-run-z5tw3oezda-rj.a.run.app/docs
Versão puxada automaticamente pelo github actions

# Funcionamento

Este repositório é API RESTfuls simples de um banco de dados de filmes, cada end-point será um método REST. O banco de dados será relacional, com uma simples tabela de filmes com uma foreign key pra os gêneros do filme. Mais detalhes dos endpoints:

Post - Create
Adiciona um filme no banco de dados após fazer validação dos paramêtros

Put - Update
Atualiza todos os dados do filme pelo id

Patch - Updade
Atualiza apenas alguns dados do filme pelo id

Delete - Delete
Apaga o filme do banco de dados pelo id

Get - Read
Ao acessar a url "/movies/" busca todos os filmes do banco de dados, opcionalmente pode fazer um query passando "?q=" e por um limite passando um "?limit="

Também adicionei um endpoint parar o id dos gêneros, pois o id é necessário para as operações de write.


# Implementações que eu faria se tivesse mais tempo

Adicionar token authentication para as operações de write

Um filme poderia ter múltiplos gêneros e também dá pra aprimorar o end-point para buscar todos os filmes de cada gênero.

Associar uma imagem a cada filme, para poder ser exibido com mais facilidade no front-end.

Adicionaria REDIS para cache, assim diminuindo a quantidade de requisições diretas no banco, que faria bastante diferença em alta escala. O REDIS ainda poderia ser utilizado como message broker num sistema de arquitetura de micro-serviços no futuro.

Integrate unit testing to the deployment workflow
