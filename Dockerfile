FROM python:3.10-alpine

ENV VIRTUAL_ENV=/venv

RUN python3 -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apk update && apk add python3-dev \
                        gcc \
                        libc-dev

# Install dependencies:
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# CMD ["uvicorn", "sql_app.main:app", "--host", "0.0.0.0", "--port", "8000"]

CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 sql_app.main:app

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]