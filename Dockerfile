FROM python:3.8-alpine AS build

WORKDIR /app

RUN apk add --no-cache --virtual .build-deps \
        build-base linux-headers gcc musl-dev libffi-dev postgresql-dev libpq && \
    pip install --upgrade pip && \
    pip install pipenv

COPY Pipfile Pipfile.lock ./
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --ignore-pipfile

COPY . .

FROM python:3.8-alpine

WORKDIR /app

RUN apk add --no-cache libpq && \
    pip install --upgrade pip && \
    pip install pipenv

COPY --from=build /app /app

ENV PIPENV_VENV_IN_PROJECT=1
ENV PATH="/app/.venv/bin:$PATH"

COPY .env /app/.env

EXPOSE 5000

CMD ["pipenv", "run", "python", "src/main.py"]
