"""
This file is used to configure the ORM settings & API Configurations.
Please do not store sensitive information in this file, this file is not for storing tokens and secret keys.
"""
import os
from datetime import datetime

import pytz


DATABASE_CONNECTION = {
    "connections": {
        "default": "sqlite://database.db"
    },
    "apps": {
        "entities": {
            "models": ["entities.users", "entities.permissions"],
            "default_connection": "default"
        }
    }
}

ORIGINS = [
    "*",
]

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_now():
    """
    Get aware datetime
    :return:
    """
    return datetime.now(tz=pytz.UTC)
