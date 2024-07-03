"""
Oxygen CS Application
This module continuously monitors a sensor hub and manages HVAC (Heating,
Ventilation, and Air Conditioning) system actions based on received sensor data.
"""

import json
import logging
import os
import time
import requests
import psycopg2
from dotenv import load_dotenv
from signalrcore.hub_connection_builder import HubConnectionBuilder


class App:
    """Class to manage HVAC system actions based on sensor data."""

    def __init__(self):
        """Initialize the App class."""
        load_dotenv()
        self._hub_connection = None
        self._db_connection = None
        self.ticks = 10
        self.host = os.getenv("HOST")
        self.token = os.getenv("TOKEN")
        self.t_max = int(os.getenv("T_MAX"))
        self.t_min = int(os.getenv("T_MIN"))
        self.database_url = os.getenv("DATABASE_URL")

    def __del__(self):
        """Cleanup resources."""
        if self._hub_connection is not None:
            self._hub_connection.stop()
        if self._db_connection is not None:
            self._db_connection.close()

    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        self._db_connection = psycopg2.connect(self.database_url)
        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """Configure hub connection and subscribe to sensor data events."""
        url = f"{self.host}/SensorHub?token={self.token}"
        print(f"Connecting to: {url}")
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(url)
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )
        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]
            temperature = float(data[0]["data"])
            event = self.take_action(temperature)
            self.save_event_to_database(timestamp, temperature, event)
        except ValueError as err:
            print(f"Error processing sensor data: {err}")

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.t_max):
            self.send_action_to_hvac("TurnOnAc")
            return "TurnOnAc"
        if float(temperature) <= float(self.t_min):
            self.send_action_to_hvac("TurnOnHeater")
            return "TurnOnHeater"
        return "DoNothing"

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        response = requests.get(
            f"{self.host}/api/hvac/{self.token}/{action}/{self.ticks}", timeout=10
        )
        details = json.loads(response.text)
        print(details, flush=True)

    def save_event_to_database(self, timestamp, temperature, event):
        """Save sensor data into database."""
        try:
            with self._db_connection.cursor() as cur:
                query = """
                INSERT INTO oxygen_temperatures (timestamp, temperature, event)
                VALUES (%s, %s, %s)
                """
                cur.execute(query, (timestamp, temperature, event))
                self._db_connection.commit()
        except psycopg2.DatabaseError as db_err:
            print(f"Database error: {db_err}")
            self._db_connection.rollback()


if __name__ == "__main__":
    app = App()
    app.start()
