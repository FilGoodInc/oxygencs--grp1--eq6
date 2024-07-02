# Utiliser une image Python de base
FROM python:3.8-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application
COPY . /app

# Installer les dépendances
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile

# Copier le fichier .env
COPY .env /app/.env

# Commande pour démarrer l'application
CMD ["pipenv", "run", "python", "src/main.py"]