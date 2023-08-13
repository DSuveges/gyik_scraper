"""Utility functions to interact with the database."""
from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from typing import TYPE_CHECKING

logger = logging.getLogger("__main__")

if TYPE_CHECKING:
    from db_connection import db_connection


class db_handler:
    """This class defines the modules to add data directly to the database.

    Contains all the SQL statements as well.
    """

    # Add new user to table:
    add_user_sql = """
        INSERT INTO USER(USER, USER_PERCENT)
        VALUES(
            :user,
            :user_percent
        )
    """

    # Update percent of an existing user:
    update_percent_sql = """
        UPDATE USER
        SET USER_PERCENT = :user_percent
        WHERE USER = :user
    """

    # Retrieve user based on username:
    get_user_sql = """SELECT * FROM USER WHERE USER = :user"""

    # Retrieve keyword:
    get_keyword_sql = """SELECT * FROM KEYWORD WHERE KEYWORD = :keyword"""

    # Add keyword:
    add_keyword_sql = """INSERT INTO KEYWORD(KEYWORD) VALUES(:keyword)"""

    # Look up question in the database based on the gyik id:
    question_lookup_sql = """SELECT * FROM QUESTION WHERE GYIK_ID = :gyik_id"""

    # Look up study in the database based on the gyik id:
    link_to_keyword_sql = """
        INSERT INTO QUESTION_KEYWORD (QUESTION_ID, KEYWORD_ID)
        VALUES(
            :question_id,
            :keyword_id
        )
    """

    # Test keyword linking:
    get_link_sql = """
        SELECT *
        FROM QUESTION_KEYWORD
        WHERE
            QUESTION_ID = :question_id AND
            KEYWORD_ID = :keyword_id
    """

    # Add question to database:
    add_question_sql = """
        INSERT INTO QUESTION (
            GYIK_ID,
            CATEGORY,
            SUBCATEGORY,
            QUESTION_TITLE,
            QUESTION,
            QUESTION_DATE,
            URL,
            USER_ID,
            ADDED_DATE
        )
        VALUES (
            :gyik_id,
            :category,
            :subcategory,
            :question_title,
            :question,
            :question_date,
            :url,
            :user_id,
            :added_date
        )
    """

    # Look up an answer in the database based on the gyik id:
    get_answer_sql = """SELECT * FROM ANSWER WHERE GYIK_ID = :gyik_id"""

    # Getting the answer count for a given question, submitted by other than OP:
    get_answer_count_sql = """
        SELECT
            COUNT (*) AS ANSWER_COUNT,
            Q.GYIK_ID
        FROM
            QUESTION as Q,
            ANSWER as A
        WHERE
            Q.ID = A.QUESTION_ID AND
            Q.GYIK_ID = :gyik_id  AND
            (
                A.USER_ID != Q.USER_ID OR
                A.USER_ID IS NULL
            )
    """

    # Inserting data to answers:
    add_answer_sql = """
        INSERT INTO ANSWER (
            GYIK_ID,
            USER_ID,
            QUESTION_ID,
            ANSWER_DATE,
            ANSWER_TEXT,
            USER_PERCENT,
            ANSWER_PERCENT
        )
        VALUES (
            :gyik_id,
            :user_id,
            :question_id,
            :answer_date,
            :answer_text,
            :user_percent,
            :answer_percent
        )
    """

    # When a question is in the database, however we want to fetch it again, we need to delete first:
    delete_question_sql = """
        DELETE FROM QUESTION
        WHERE GYIK_ID = :gyik_id
    """

    def __init__(self: db_handler, connection: db_connection) -> None:
        """Initialize the db handler object.

        Args:
            self (db_handler)
            connection (db_connection): The `connection` parameter is an object representing a connection
        to a database. It is expected to be an instance of the `sqlite3.Connection` class, which is a
        connection object provided by the `sqlite3` module in Python. This connection object is used to
        interact with the database and execute SQL
        """
        if not isinstance(connection, sqlite3.Connection):
            raise TypeError(
                f"Connection object is expected for initialize add_data object. Got type: {type(connection)}."
            )

        self.conn = connection
        self.cursor = connection.cursor()

    def link_to_keyword(self: db_handler, question_id: int, keyword_id: int) -> None:
        """Check if a link between a question and a keyword exists, and if not, adds the link.

        Args:
            question_id (int): The `question_id` identifies question in the database.
            keyword_id (int): The `keyword_id` identifies keyword in the database.
        """
        # Does the link exists?
        self.cursor.execute(
            self.get_link_sql, {"question_id": question_id, "keyword_id": keyword_id}
        )

        # Add link if not yet in the database:
        if not self.cursor.fetchone():
            self.cursor.execute(
                self.link_to_keyword_sql,
                {"question_id": question_id, "keyword_id": keyword_id},
            )
        else:
            logger.warning("Question/keyword link already exist.")

    def add_user(self: db_handler, user: str, percent: float) -> int | None:
        """Get user ID or adds to db if not aready in the db.

        Also updates percent if missing in db, but in the query. If

        Args:
            self (db_handler, user)
            user (str): user name
            percent (float): percent value of the usefulness of the answers
        Returns:
            int: identifier of the user in the database.
        """
        # Fetch data from db:
        self.cursor.execute(self.get_user_sql, {"user": user})

        # The user is in the database:
        try:
            # Parsing row:
            (ID, _, USER_PERCENT) = self.cursor.fetchone()

            # If percent is missing, let's update:
            if percent and not USER_PERCENT:
                self.cursor.execute(
                    self.update_percent_sql, {"user": user, "user_percent": percent}
                )

        # If user is not in the database we add it:
        except TypeError:
            self.cursor.execute(
                self.add_user_sql, {"user": user, "user_percent": percent}
            )
            ID = self.cursor.lastrowid

        # Return with the ID
        if not isinstance(ID, int):
            raise TypeError(
                f"Could not insert new user into database: {user}, returned id: {ID}"
            )
        return int(ID)

    def add_keyword(self: db_handler, keyword: str) -> int:
        """Testing if keyword exists. If no, adds to database.

        Args:
            self (db_handler)
            keyword (str): keyword parsed from html
        Returns:
            str keyword ID in the database.
        """
        # None values cannot be added:
        if not keyword:
            raise ValueError("Keyword must be specified!")

        # Fetch data from db:
        self.cursor.execute(self.get_keyword_sql, {"keyword": keyword})

        # The keyword is in the database:
        try:
            # Parsing row:
            (ID, _) = self.cursor.fetchone()

        # If user is not in the database we add it:
        except TypeError:
            self.cursor.execute(self.add_keyword_sql, {"keyword": keyword})
            ID = self.cursor.lastrowid

        if not isinstance(ID, int):
            raise ValueError(
                f"Could not insert keyword ({keyword}) into the database. Id: {ID}"
            )

        # Return with the ID
        return ID

    def test_question(self: db_handler, gyik_id: int) -> bool:
        """Tests if question is already in the database by GYIK_ID.

        Args:
            self (db_handler)
            gyik_id (str): GYIK identifier of a question
        Returns:
            bool: True if question is already in the database, False if not
        """
        # Fetch data from db:
        self.cursor.execute(self.question_lookup_sql, {"gyik_id": gyik_id})

        # The question is in the database:
        if self.cursor.fetchone():
            return True
        else:
            return False

    def get_answer_count(self: db_handler, gyik_id: int) -> int | None:
        """Tests if question is already in the database by GYIK_ID.

        Args:
            self (db_handler)
            gyik_id (str): GYIK identifier of a question
        Returns:
            int | None: Then number of answers are returned or None if the question is not in database
        """
        # Fetch data from db:
        self.cursor.execute(self.question_lookup_sql, {"gyik_id": gyik_id})
        (count, question_id) = self.cursor.fetchone()

        # Is the id value none:
        if question_id is None:
            return None
        else:
            return count

    def add_question(self: db_handler, question_data: dict) -> int:
        """Add a new row to the question table.

        Args:
            self (db_handler)
            question_data (dict): parsed data organized into a dictionary and added
        Returns:
            int identifier of the newly inserted question, None if question is already in the database
        """
        # Test if data is in a proper type:
        if not isinstance(question_data, dict):
            raise TypeError("Question data must be a dictionary")

        # Test if all required values exist:
        for field in [
            "URL",
            "GYIK_ID",
            "TITLE",
            "CATEGORY",
            "SUBCATEGORY",
            "QUESTION",
            "QUESTION_DATE",
            "USER_ID",
        ]:
            if field not in question_data:
                raise KeyError("Question data must contain key: {}".format(field))

        # Submit query:
        d = {
            "gyik_id": question_data["GYIK_ID"],
            "category": question_data["CATEGORY"],
            "subcategory": question_data["SUBCATEGORY"],
            "question_title": question_data["TITLE"],
            "question": question_data["QUESTION"],
            "question_date": question_data["QUESTION_DATE"],
            "url": question_data["URL"],
            "user_id": question_data["USER_ID"],
            "added_date": datetime.now(),
        }
        self.cursor.execute(self.add_question_sql, d)
        question_id = self.cursor.lastrowid

        # Raising type error if insertion got failed:
        if not isinstance(question_id, int):
            raise TypeError(f"Failed to insert new row into database: {question_id}")

        return question_id

    def test_answer(self: db_handler, gyik_id: int) -> bool:
        """Test if the gyik ID of the answer exist.

        Args:
            self (db_handler)
            gyik_id (int): integer value of the gyik identifer of the answer
        Returns:
            boolean indicating if the answer is already there (True) or not (False)
        """
        # Fetch data from db:
        self.cursor.execute(self.get_answer_sql, {"gyik_id": gyik_id})

        # The question is in the database:
        if self.cursor.fetchone():
            return True
        else:
            return False

    def add_answer(self: db_handler, answer_data: dict) -> int | None:
        """
        This methods adds a new row to the question data
        """

        # Test input data:
        if not isinstance(answer_data, dict):
            raise TypeError("Answer data must be a dictionary")

        # Test if all required values exist:
        for field in [
            "USER_ID",
            "GYIK_ID",
            "ANSWER_DATE",
            "ANSWER_TEXT",
            "ANSWER_PERCENT",
            "USER_PERCENT",
        ]:
            if field not in answer_data:
                raise KeyError("Answer data must contain key: {}".format(field))

        # Test if this question is already in the database:
        if self.test_answer(answer_data["GYIK_ID"]):
            logger.warning(
                f'This question ({answer_data["GYIK_ID"]}) has already been added to the database! Skipping'
            )
            return None

        # Submit query:
        d = {
            "gyik_id": answer_data["GYIK_ID"],
            "answer_date": answer_data["ANSWER_DATE"],
            "answer_text": answer_data["ANSWER_TEXT"],
            "user_percent": answer_data["USER_PERCENT"],
            "answer_percent": answer_data["ANSWER_PERCENT"],
            "question_id": answer_data["QUESTION_ID"],
            "user_id": answer_data["USER_ID"],
        }
        self.cursor.execute(self.add_answer_sql, d)

        return self.cursor.lastrowid

    def commit(self: db_handler) -> None:
        """Commit changes in the database.

        Args:
            self (db_handler)
        """
        self.conn.commit()

    def rollback(self: db_handler) -> None:
        """Roll back changes in the database.

        Args:
            self (db_handler)
        """
        self.conn.rollback()

    def close(self: db_handler) -> None:
        """Close connection to the databse.

        Args:
            self (db_handler)
        """
        self.conn.close()


class question_loader:
    """This class loads data of a full question (question, keywords, answers etc) into the database.

    There is a very specific order in which the data can be loaded into the database.
    """

    def __init__(self: question_loader, db_handler: db_handler) -> None:
        """Initialize object with db_handler. When data is subsequently added, this handler is going to be called.

        Args:
            self (question_loader)
            db_handler (db_handler): The `db_handler`
        """
        # Storing db_handler:
        self.db_obj = db_handler

    def add_question(self: question_loader, question_data: dict) -> None:
        """Once all components of the question is parsed and the proper data structure built load to database.

        Args:
            self (question_loader)
            question_data (dict): all data captrured for a question (eg. text and answers) modelled as a dictionary
        """
        # 1. Adding user - person who asked the question is often not available. If yes, we add to the db.
        if not question_data["USER"]["USER"]:
            question_data["USER_ID"] = None
        else:
            question_data["USER_ID"] = self.db_obj.add_user(
                question_data["USER"]["USER"], question_data["USER"]["USER_PERCENT"]
            )

        # 2. Add question
        question_id = self.db_obj.add_question(question_data)

        # Loop through all keywords:
        for keyword in question_data["KEYWORDS"]:
            if not keyword or keyword is None or keyword == "":
                continue

            # Add keyword:
            keyword_id = self.db_obj.add_keyword(keyword)

            # Add question links to keyword:
            self.db_obj.link_to_keyword(question_id, keyword_id)

        # Loop through all answers:
        for answer in question_data["ANSWERS"]:
            # Adding question id as foreign key pointing to the question table:
            answer["QUESTION_ID"] = question_id

            # Add users to answer object:
            if answer["USER"]["USER"]:
                answer["USER_ID"] = self.db_obj.add_user(
                    answer["USER"]["USER"], answer["USER"]["USER_PERCENT"]
                )
            else:
                answer["USER_ID"] = None

            # Add answer to the database:
            self.db_obj.add_answer(answer)

        # The changes are only committed after all uploads were successfully completed.
        self.db_obj.commit()
