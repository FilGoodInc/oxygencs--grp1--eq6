import logging
import requests
import json
import time
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
from signalrcore.hub_connection_builder import HubConnectionBuilder


class App:
    def __init__(self):
        load_dotenv()
        self._hub_connection = None
        self._db_connection = None
        self.TICKS = 10
        self.HOST = os.getenv('HOST')
        self.TOKEN = os.getenv('TOKEN')
        self.T_MAX = int(os.getenv('T_MAX'))
        self.T_MIN = int(os.getenv('T_MIN'))
        self.DATABASE_URL = os.getenv('DATABASE_URL')

    def __del__(self):
        if self._hub_connection != None:
            self._hub_connection.stop()
        if self._db_connection is not None:
            self._db_connection.close()

    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        self._db_connection = psycopg2.connect(self.DATABASE_URL)
        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """Configure hub connection and subscribe to sensor data events."""
        url = f"{self.HOST}/SensorHub?token={self.TOKEN}"
        print(f"Connecting to: {url}")  # Debug print
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
        except Exception as err:
            print(err)

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.T_MAX):
            self.send_action_to_hvac("TurnOnAc")
            return "TurnOnAc"
        elif float(temperature) <= float(self.T_MIN):
            self.send_action_to_hvac("TurnOnHeater")
            return "TurnOnHeater"
        return "DoNothing"

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{self.TICKS}")
        details = json.loads(r.text)
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
            pass
        except requests.exceptions.RequestException as e:
            self._db_connection.rollback()
            pass


if __name__ == "__main__":
    app = App()
    app.start()
