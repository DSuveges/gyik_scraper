"""Main orcestrator logic to scrape data from gyakorikerdesek.hu."""
from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from typing import TYPE_CHECKING, List

from db_tools.db_connection import db_connection
from db_tools.db_utils import db_handler, question_loader
from scraper import download_page, parse_full_question, parser_helper
from scraper.parser_helper import get_all_questions, get_last_question_page

if TYPE_CHECKING:
    from argparse import Namespace

# Core URL:
URL = "https://www.gyakorikerdesek.hu"


class GyikScraper(object):
    """This class orcestrates all three stages of the parser.

    1. fetching html from website.
    2. parse relevant information.
    3. Upload data to database.
    """

    def __init__(self: GyikScraper, connection: db_connection) -> None:
        """Initialize by providing the database connection object. With the database object, a loader object is initialized.

        Args:
            self (GyikScraper)
            connection (db_connection): object with tools to interact with the database
        """
        self.db_handler = db_handler(connection.conn)
        self.question_loader = question_loader(self.db_handler)

    def scrape_question(self: GyikScraper, URL: str) -> None:
        """Scrape a single question and add to the database without checking.

        Args:
            self (GyikScraper)
            URL (str): URL pointing to the question
        """
        # Feth data:
        retrieved_question = parse_full_question.retrieve_question(URL)

        # Parse data:
        parsed_data = retrieved_question.get_data()

        # Add data to database:
        self.question_loader.add_question(parsed_data)

    def scrape_question_list(self: GyikScraper, question_list: List[tuple]) -> None:
        """Walk through a list of URLs pointing to question and parse data and add to database.

        This method also checks if the question is already in the database or update is needed.

        Args:
            self (GyikScraper)
            question_list (list): list of questions by their URL to scrape
        """
        # Looping through the list of URLs:
        for question_url, answer_count, gyik_id in question_list:
            # 1. Get counts from database:
            answer_count_db = self.db_handler.get_answer_count(gyik_id)

            # 2. The question is new, scrape question:
            if answer_count_db is None:
                self.scrape_question(question_url)
            # 3. The question has the same number of answer as what we have in the database:
            elif answer_count_db == answer_count:
                logging.warning(
                    f"Question ({gyik_id}) ingested. Number of answers is the same ({answer_count_db})."
                )
                continue
            # Although the question is in the database the number of answers is different:
            else:
                logging.info(
                    f"Question ({gyik_id}) has new answers: {answer_count_db} -> {answer_count}"
                )
                # TODO: fix deletion logic. However, strictly speaking, this is not needed. becauce the uniqueness of the Gyik id of the answer is also checket
                # 4. Drop question from database: <- there's something problematic with the delete.
                # self.db_handler.drop_question(gyik_id)
                # 5. Ingesting the question again:
                self.scrape_question(question_url)


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
    scraper_object = GyikScraper(database_connection)

    # Only one page is parsed if direct question is passed:
    if direct_question:
        logging.info(f"Fetching single question: {direct_question}")
        scraper_object.scrape_question(direct_question)
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
        questions = get_all_questions(soup)
        # print(questions)
        # sys.exit()

        # Retrieve all question data:
        scraper_object.scrape_question_list(questions)

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
    parser.add_argument("--category", type=str, help="Main category.", required=False)
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
        handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
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
