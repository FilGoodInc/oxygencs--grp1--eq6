"""
Integration tests for the App class in the src.main module.
"""

import os
import pytest
from dotenv import load_dotenv
import requests_mock
import psycopg2
from src.main import App

load_dotenv(dotenv_path=".env.test")


@pytest.fixture(scope="module")
def db_connection():
    """Fixture for creating a database connection."""
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def app_instance(db_connection):
    """Fixture for creating an instance of the App class."""
    app = App()
    app._db_connection = db_connection
    return app


@pytest.fixture
def mock_requests():
    """Fixture for mocking HTTP requests."""
    with requests_mock.Mocker() as m:
        yield m


def test_sensor_data_received(db_connection, app_instance, mock_requests):
    """Test receiving sensor data and saving it to the database."""
    mock_requests.get(
        f"{app_instance.host}/api/hvac/{app_instance.token}/TurnOnAc/{app_instance.ticks}",
        text='{"status": "success"}',
    )
    mock_requests.get(
        f"{app_instance.host}/api/hvac/{app_instance.token}/TurnOnHeater/{app_instance.ticks}",
        text='{"status": "success"}',
    )

    sensor_data = [{"date": "2024-07-01T12:00:00Z", "data": "35"}]
    app_instance.on_sensor_data_received(sensor_data)

    with db_connection.cursor() as cur:
        cur.execute(
            "SELECT timestamp, temperature, event FROM oxygen_temperatures WHERE timestamp = %s",
            ("2024-07-01T12:00:00Z",),
        )
        result = cur.fetchone()
        assert result is not None
        assert result[0].isoformat() == "2024-07-01T12:00:00"
        assert result[1] == 35.0
        assert result[2] == "TurnOnAc"
