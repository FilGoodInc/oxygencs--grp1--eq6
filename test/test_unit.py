"""Tests for the App class."""

from unittest.mock import patch, MagicMock
import pytest
from src.main import App


@pytest.fixture
def app_instance():
    """Fixture for creating an instance of App."""
    app = App()
    app._db_connection = MagicMock()
    return app


def test_init(app_instance):
    """Test the initialization of the App class."""
    assert app_instance.ticks == 10


def test_take_action_ac(app_instance):
    """Test the take_action method for AC activation."""
    action = app_instance.take_action(30)
    assert action == "TurnOnAc"


def test_take_action_heater(app_instance):
    """Test the take_action method for heater activation."""
    action = app_instance.take_action(10)
    assert action == "TurnOnHeater"


def test_take_action_nothing(app_instance):
    """Test the take_action method for no action."""
    action = app_instance.take_action(20)
    assert action == "DoNothing"


def test_save_event_to_database(app_instance):
    """Test the save_event_to_database method."""
    with patch.object(
        app_instance._db_connection, "cursor", create=True
    ) as mock_cursor:
        app_instance.save_event_to_database("2023-01-01T00:00:00", 25.0, "TurnOnAc")
        mock_cursor.assert_called_once()
