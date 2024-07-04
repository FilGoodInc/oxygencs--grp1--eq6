FROM python:3.8-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip \
    && pip install pipenv

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --ignore-pipfile

COPY .env /app/.env

ENV PIPENV_VENV_IN_PROJECT=1
ENV PATH="/app/.venv/bin:$PATH"

CMD ["pipenv", "run", "python", "src/main.py"]
