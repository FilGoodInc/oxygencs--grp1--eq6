# LOG-680 : Template for Oxygen-CS

This Python application continuously monitors a sensor hub and manages HVAC (Heating, Ventilation, and Air Conditioning) system actions based on received sensor data.

It leverages `signalrcore` to maintain a real-time connection to the sensor hub and utilizes `requests` to send GET requests to a remote HVAC control endpoint.

This application uses `pipenv`, a tool that aims to bring the best of all packaging worlds to the Python world.

## Requirements

- Python 3.8+
- pipenv

## Getting Started

Install the project's dependencies:

```bash
pipenv install
```

## Running the Program

After setup, you can start the program with the following command:

```bash
pipenv run start
```

## Logging

The application logs important events such as connection open/close and error events to help in troubleshooting.

## To Implement

There are placeholders in the code for sending events to a database and handling request exceptions. These sections should be completed as per the requirements of your specific application.

## Docker

### Building the Docker Image

Build the Docker image with the following command:

```bash
sudo docker build -t oxygencs-grp1-eq6:latest .
```

### Testing the Docker Image Locally

Test the Docker image locally by mapping the port and using the `.env` file:

```bash
sudo docker run --env-file .env oxygencs-grp1-eq6:latest
```

### Tagging the Docker Image

Tag the Docker image for DockerHub:

```bash
sudo docker tag oxygencs-grp1-eq6:latest log680equipe6ete24/oxygencs-grp1-eq6:latest
```

### Pushing the Docker Image to DockerHub

Log in to DockerHub and push the image:

```bash
sudo docker login
sudo docker push log680equipe6ete24/oxygencs-grp1-eq6:latest
```

### Verifying Deployment from DockerHub

1. Pull the Docker image from DockerHub:

    ```bash
    sudo docker pull log680equipe6ete24/oxygencs-grp1-eq6:latest
    ```

2. Run the Docker image with the port mapping:

    ```bash
    sudo docker run --env-file .env -p 5000:5000 log680equipe6ete24/oxygencs-grp1-eq6:latest
    ```

3. Access the application:

    Open your browser and go to `http://localhost:5000` or `http://127.0.0.1:5000` to verify that the application is working correctly.

## License

MIT

## Contact

For more information, please feel free to contact the repository owner.

# Configuration de l'application

## Variables d'environnement

L'application utilise les variables d'environnement suivantes, configurées dans un fichier `.env` :

- `HOST` : Adresse de l'habitation
- `TOKEN` : Token de la pièce
- `T_MAX` : Température maximale
- `T_MIN` : Température minimale
- `DATABASE_URL` : URL de connexion à la base de données

## Exemple de fichier .env

```env
HOST=example_host
TOKEN=example_token
T_MAX=25
T_MIN=18
DATABASE_URL=postgresql://user:password@localhost:5432/mydatabase
```