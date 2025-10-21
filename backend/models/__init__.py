#!/usr/bin/env python3

"""
Initializes database storage based on the current environment.
"""

from dotenv import load_dotenv
import os

from models.engine.dbstorage import DBStorage

load_dotenv()

database_url_prod = os.getenv("DATABASE_URL_PROD")
database_url_test = os.getenv("DATABASE_URL_TEST")
database_url_dev = os.getenv("DATABASE_URL_DEV")

if os.getenv("ENV") == "prod":
    if not database_url_prod:
        raise ValueError(
            "No environment variable for production database url"
        )
    database_url = database_url_prod
elif os.getenv("ENV") == "test":
    if not database_url_test:
        raise ValueError(
            "No environment variable for test database url"
        )
    database_url = database_url_test
else:
    if not database_url_dev:
        raise ValueError(
            "No environment variable for development database url"
        )
    database_url = database_url_dev

storage = DBStorage(database_url)
storage.reload()
