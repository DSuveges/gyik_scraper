"""Toolset for the lowest level interaction with the database."""
from __future__ import annotations

import logging
import os.path
import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlite3 import Connection

logger = logging.getLogger("__main__")


class db_connection:
    """This class establishes the connection with the database. It also has the table definitions.

    If the requested db file does not exist, creates the database with the proper tables.
    """

    # The table in which the potential keywords are stored for a question:
    keyword_table_sql = """CREATE TABLE IF NOT EXISTS KEYWORD (
        ID INTEGER PRIMARY KEY,
        KEYWORD TEXT NOT NULL
    )"""

    # Table with all the user information is available:
    user_table_sql = """CREATE TABLE IF NOT EXISTS USER (
        ID INTEGER PRIMARY KEY,
        USER TEXT NOT NULL,
        USER_PERCENT NUMERIC
    )"""

    # Table in which we store question data:
    question_table_sql = """CREATE TABLE IF NOT EXISTS QUESTION (
        ID INTEGER PRIMARY KEY,
        GYIK_ID INTEGER NOT NULL,
        CATEGORY TEXT NOT NULL,
        SUBCATEGORY TEXT NOT NULL,
        QUESTION_TITLE TEXT NOT NULL,
        QUESTION TEXT,
        QUESTION_DATE DATETIME NOT NULL,
        URL TEXT NOT NULL,
        USER_ID INTEGER,
        ADDED_DATE DATETIME NOT NULL,
        FOREIGN KEY (USER_ID) REFERENCES USER (ID)
    )"""

    # Table with the answers:
    answer_table_sql = """CREATE TABLE IF NOT EXISTS ANSWER (
        ID INTEGER PRIMARY KEY,
        USER_ID INTEGER,
        GYIK_ID INTEGER NOT NULL,
        QUESTION_ID INTEGER NOT NULL,
        ANSWER_DATE DATETIME NOT NULL,
        ANSWER_TEXT TEXT NOT NULL,
        USER_PERCENT NUMERIC,
        ANSWER_PERCENT NUMERIC,
        FOREIGN KEY (USER_ID) REFERENCES USER (ID),
        CONSTRAINT QUESTION_ID
            FOREIGN KEY (QUESTION_ID)
            REFERENCES QUESTION (ID)
            ON DELETE CASCADE
    )"""

    # Linking table making connection between questions and keywords:
    question_keyword_table_sql = """CREATE TABLE IF NOT EXISTS QUESTION_KEYWORD (
        KEYWORD_ID INTEGER NOT NULL,
        QUESTION_ID INTEGER NOT NULL,
        FOREIGN KEY (KEYWORD_ID) REFERENCES KEYWORD (ID),
        CONSTRAINT QUESTION_ID
            FOREIGN KEY (QUESTION_ID)
            REFERENCES QUESTION (ID)
            ON DELETE CASCADE
    )"""

    def __init__(self: db_connection, filename: str) -> None:
        """Initialize a database connection.

        - Check if a file exists,
        - Creates a connection to the file
        - Creates all necessary tables if new db is created.

        Args:
            self (db_connection)
            filename (str): Name of the file representing the database.
        """
        # Check if file exists:
        if not os.path.isfile(filename):
            logger.info(f"{filename} could not be opened. DB is being created.")

        # Create connection:
        connection = self._create_connection(filename)
        self.conn = connection

        # Create all tables:
        self._create_all_tables()

    def _create_connection(self: db_connection, db_file: str) -> Connection:
        """Create a database connection to the SQLite database specified by db_file.

        Args:
            self (db_connection)
            db_file (str): database file name
        """
        try:
            return sqlite3.connect(db_file)
        except ConnectionError:
            logger.error(f"[Error] DB could not be connected ({db_file}). Exiting")
            raise ConnectionError(
                f"[Error] DB could not be connected ({db_file}). Exiting"
            )

    def _create_table(self: db_connection, create_table_sql: str) -> None:
        """Create a table from the create_table_sql statement.

        Args:
            self (db_connection)
            create_table_sql (str): a CREATE TABLE statement
        """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except ConnectionError:
            logger.error("Table could not be created.")
            raise ConnectionError("Table could not be created.")

    def _create_all_tables(self: db_connection) -> None:
        """Create ALL tables required by the database.

        Args:
            self (db_connection)
        """
        tables_to_create = ["keyword", "user", "question", "answer", "question_keyword"]

        # create all tables
        for table in tables_to_create:
            sql_statement = getattr(self, table + "_table_sql")
            self._create_table(sql_statement)
