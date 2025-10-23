#!/usr/bin/env python3

"""
Initializes database storage based on the current environment.
"""

from dotenv import load_dotenv
import os

from models.engine.dbstorage import DBStorage

load_dotenv()

def setup_production_database() -> str:
    """
    """
    database_user = os.getenv("POSTGRES_USER")
    database_password = os.getenv("POSTGRES_PASSWORD")
    database_name = os.getenv("POSTGRES_NAME")
    database_host = os.getenv("POSTGRES_HOST")
    database_port = os.getenv("POSTGRES_PORT")

    if not database_user:
        raise ValueError(
            "No environment variable for production database user."
        )
    if not database_password:
        raise ValueError(
            "No environment variable for production database password."
        )
    if not database_name:
        raise ValueError(
            "No environment variable for production database name."
        )
    if not database_host:
        raise ValueError(
            "No environment variable for production database host."
        )
    if not database_port:
        raise ValueError(
            "No environment variable for production database port."
        )

    database_url = (
        f"postgresql+psycopg2://{database_user}:{database_password}"
        f"@{database_host}:{database_port}/{database_name}"
    )
    return database_url

def setup_test_database() -> str:
    """
    """
    test_database_user = os.getenv("TEST_DATABASE_USER")
    test_database_password = os.getenv("TEST_DATABASE_PASSWORD")
    test_database_name = os.getenv("TEST_DATABASE_NAME")
    test_database_host = os.getenv("TEST_DATABASE_HOST")
    test_database_port = os.getenv("TEST_DATABASE_PORT")

    if not test_database_user:
        raise ValueError(
            "No environment variable for test database user."
        )
    if not test_database_password:
        raise ValueError(
            "No environment variable for test database password."
        )
    if not test_database_name:
        raise ValueError(
            "No environment variable for test database name."
        )
    if not test_database_host:
        raise ValueError(
            "No environment variable for test database host."
        )
    if not test_database_port:
        raise ValueError(
            "No environment variable for test database port."
        )

    test_database_url = (
        f"postgresql+psycopg2://{test_database_user}:{test_database_password}"
        f"@{test_database_host}:{test_database_port}/{test_database_name}"
    )
    return test_database_url

def setup_developement_database() -> str:
    """
    """
    dev_database_user = os.getenv("DEV_DATABASE_USER")
    dev_database_password = os.getenv("DEV_DATABASE_PASSWORD")
    dev_database_name = os.getenv("DEV_DATABASE_NAME")
    dev_database_host = os.getenv("DEV_DATABASE_HOST", "localhost")
    dev_database_port = os.getenv("DEV_DATABASE_PORT", "5432")

    if not dev_database_user:
        raise ValueError(
            "No environment variable for test database user."
        )
    if not dev_database_password:
        raise ValueError(
            "No environment variable for test database password."
        )
    if not dev_database_name:
        raise ValueError(
            "No environment variable for test database name."
        )
    if not dev_database_host:
        raise ValueError(
            "No environment variable for test database host."
        )
    if not dev_database_port:
        raise ValueError(
            "No environment variable for test database port."
        )

    dev_database_url = (
        f"postgresql+psycopg2://{dev_database_user}:{dev_database_password}"
        f"@{dev_database_host}:{dev_database_port}/{dev_database_name}"
    )
    return dev_database_url


if os.getenv("ENV") == "development":
    database_url = setup_developement_database()
elif os.getenv("ENV") == "test":
    database_url = setup_test_database()
else:
    database_url = setup_production_database()

storage = DBStorage(database_url)
storage.reload()
