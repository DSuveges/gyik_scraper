"""Main orcestrator logic to scrape data from gyakorikerdesek.hu."""
from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from typing import TYPE_CHECKING, List, Tuple

from db_tools.db_connection import db_connection
from db_tools.db_utils import db_handler, question_loader
from scraper import download_page, parse_full_question, parser_helper
from scraper.parser_helper import get_last_question_page

if TYPE_CHECKING:
    from argparse import Namespace

# Core URL:
URL = "https://www.gyakorikerdesek.hu"


class scraper(object):
    """This class orcestrates all three stages of the parser:

    1. fetching html from website.
    2. parse relevant information.
    3. Upload data to database.
    """

    def __init__(self, connection: db_connection) -> None:
        """Initialize by providing the database connection object. With the database object, a loader object is initialized.

        Args:
            self (scraper)
            connection (db_connection): object with tools to interact with the database
        """
        self.db_handler = db_handler(connection.conn)
        self.question_loader = question_loader(self.db_handler)

    def scrape_questions(self: scraper, URL_list: List[str]) -> None:
        """Walk through a list of URLs pointing to question and parse data and add to database.

        Args:
            self (scraper)
            URL_list (list): list of questions by their URL to scrape
        """
        # Test input: <- This is not needed.
        if not isinstance(URL_list, list):
            logging.error(
                f"scraper.get_all_questions requires a list input. {type(URL_list)} is given."
            )
            logging.error("Input data:\n")
            logging.error(URL_list)
            raise TypeError

        answer_count = self.db_obj.get_answer_count()
        """
        c = conn.conn.execute(get_answer_count_sql, {'gyik_id' : question[2]})
        counts = c.fetchone()

        # Handling output:
        if counts[1] is None:
            print(f'Question ID: {question[2]} is new!')
            # Ingest_logic
        elif counts[0] == question[1]:
            print(f'Question ID: {question[2]} already ingested. Nothing to do.')
            # Continue
        else:
            print(f'Question ({question[2]}) is already ingested but new answers arrived ({counts[0]} vs {question[1]})!')
            # Delete logic
            # Ingest logic
        """

        # Looping through URLs:
        for URL in URL_list:
            # Testing if question is loaded into the database:
            match = re.search("__(\d+)-", URL)
            if self.test_question(match[1]):
                logging.warning(f"Question is already in the database: {URL}")
                continue

            # Fetching question based on question URL:
            rq = parse_full_question.retrieve_question(URL)
            data = rq.get_data()

            # Load data:
            self.ql.add_question(data)

    def test_answer_count(self, GYIK_ID: int) -> Tuple[int, int]:
        """Get the number of answers for a given question based on GYIK_ID.

        Args:
            GYIK_ID int: GYIK identifier of a question

        return:
            Tuple where first element is the number of answers the second is the gyik id
        """
        return self.ad_obj.get_answer_count(GYIK_ID)


def __main__(
    database_file: str,
    start_page: int | None,
    end_page: int | None,
    url_path: str | None,
    direct_question: str | None,
) -> None:
    """The main function of the GYIK scraper application.

    User can specify the category, start page, end page and the database file into which
    the data is saved.

    Args:
        database_file (str): file representation of sqlite database. If not exists will be created.
        start_page (int): first page of the list of questions.
        end_page (int): last page of list of questions.
        url_path (str): path to reach the questions.
        direct_question (str): path to a single question to fetch.
    """
    # Open database, create connection, initialize loader object:
    database_connection = db_connection(database_file)  # DB connection
    scraper_object = scraper(database_connection)

    # Only one page is parsed if direct question is passed:
    if direct_question:
        logging.info(f"Fetching single question: {direct_question}")
        scraper_object.get_all_questions([direct_question])
        sys.exit()

    logging.info("Fetching data started...")

    # At this point we have to make sure start and end pages are not Null:
    assert (
        start_page is not None and end_page is not None
    ), "Start and end pages needs to be specified."

    # Looping through all defined pages:
    for page in range(start_page, end_page + 1):
        # Fetch page with questions:
        question_list_page_url = "{}/{}__oldal-{}".format(URL, url_path, page)
        soup = download_page.download_page(question_list_page_url)

        # Get URLs for all questions:
        questions = scraper_object.get_all_questions(soup)

        # Retrieve all question data:
        scraper_object.get_all_questions(questions)

        logging.info(f"page completed: {question_list_page_url}")

    logging.info("Scarping completed.")


def parse_arguments() -> Namespace:
    """Parse command line parameters.

    Returns:
        Namespace: parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="This script fetches data from http://gyakorikerdesek.hu and feeds into an SQLite database."
    )
    parser.add_argument(
        "--category", type=str, help="Main category. Mandatory", required=True
    )
    parser.add_argument(
        "--startPage",
        type=int,
        help="Start page of the question list",
        required=False,
        default=1,
    )
    parser.add_argument(
        "--endPage", type=int, help="end page of the question list.", required=False
    )
    parser.add_argument(
        "--directQuestion",
        type=str,
        help="direct link to scrape to a specific question",
        required=False,
    )
    parser.add_argument(
        "--database",
        type=str,
        help="Email address where the notification is sent.",
        required=True,
    )
    parser.add_argument(
        "--subCategory",
        type=str,
        help="Subcategory within the category.",
        required=False,
    )
    parser.add_argument(
        "--logFile",
        type=str,
        help="File into which the logs are saved",
        required=False,
        default="scraper.log",
    )
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line parameters:
    args = parse_arguments()

    database_file = os.path.abspath(args.database)
    category = args.category
    start_page = args.startPage if args.startPage is not None else 1
    sub_category = args.subCategory
    direct_question = args.directQuestion
    end_page = args.endPage

    # Set up logging:
    logging.basicConfig(
        filename=args.logFile,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Initialize empty string pointing to a :
    url_path: str = ""

    # If no direct question is given, at least category needs to be provided:
    if direct_question is None:
        assert category is not None, "Category needs to be specified."

        # URL path is changed depending if subcategory is provided or not:
        url_path = f"{category}__{sub_category}" if sub_category else category

    # Some extra logic and checks needs to be done if a range of questions is expected:
    if (direct_question is None) and (end_page is None):
        # One page is retrieved to determine if the category_subcategory pair is valid or not:
        test_page = download_page.download_page("{}/{}".format(URL, url_path))

        # If the end page is not defined, we fetch the last page from the page list:
        end_page = get_last_question_page(test_page)

    # If no direct question is given, the boundaries have to be checked:
    if direct_question is None:
        assert (
            start_page <= end_page
        ), f"The endPage ({start_page}) must be lower than end page ({end_page})"

    # Log startup parameters:
    logging.info(f"Data saved into file: {database_file}")

    if direct_question is not None:
        logging.info(f"Fetching question: {direct_question}")
    else:
        logging.info(f"Category: {category}")
        if sub_category is not None:
            logging.info(f"Subcategory: {sub_category}")
        logging.info(f"First page of questions: {start_page}")
        logging.info(f"Last page of questions: {end_page}")

    # Call main function that does stuff:
    __main__(
        database_file,
        start_page,
        end_page,
        url_path,
        direct_question,
    )
