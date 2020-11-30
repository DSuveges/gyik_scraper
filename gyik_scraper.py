from scraper import download_page
from scraper import parse_full_question
from scraper import parser_helper

from db_tools import db_connection
from db_tools import db_utils

import argparse
import re
import sys
import os
import logging


class scraper(object):
    """
    This class orcestrates all three stages of the parser:
    1. fetching html from website.
    2. parse relevant information.
    3. Upload data to database.
    """

    def __init__(self, db_obj):
        """
        Initializing by providing the database object.
        With the database object, a loader object is initialized.
        """
        self.ad_obj = db_utils.db_handler(db_obj.conn) #
        self.ql = db_utils.question_loader(self.ad_obj) # Question loader


    def get_all_questions(self, URL_list):
        """
        This method walks through a list of URLs pointing to question
        and parse data and add to databasel
        """

        # Test input:
        if not isinstance(URL_list, list):
            logging.error(f'scraper.get_all_questions requires a list input. {type(URL_list)} is given.')
            logging.error('Input data:\n')
            logging.error(URL_list)
            raise TypeError

        # Looping through URLs:
        for URL in URL_list:

            # Testing if question is loaded into the database:
            match = re.search('__(\d+)-',URL)
            if self.test_question(match[1]): 
                logging.warning(f'Question is already in the database: {URL}')
                continue

            # Fetching question based on question URL:
            rq = parse_full_question.retrieve_question(URL)
            data = rq.get_data()

            # Load data:
            self.ql.add_question(data)


    def test_question(self,GYIK_ID):
        """
        Testing if a questin is already loaded into the database or not.
        return: bool
        """
        return self.ad_obj.test_question(GYIK_ID)


def __main__():
    """
    The main function of the GYIK scraper application.
    User can specify the category, start page, end page and the database file into which
    the data is saved.
    """

    # Core URL:
    URL = 'https://www.gyakorikerdesek.hu'

    parser = argparse.ArgumentParser(description="This script fetches data from http://gyakorikerdesek.hu and feeds into an SQLite database.")
    parser.add_argument('--category', type=str, help='Main category. Mandatory', required = True)
    parser.add_argument('--startPage', type=int, help='Start page of the question list', required = False, default = 0)
    parser.add_argument('--endPage', type=int, help='end page of the question list.', required = False)
    parser.add_argument('--directQuestion', type = str, help ='direct link to scrape to a specific question', required = False)
    parser.add_argument('--database', type=str, help='Email address where the notification is sent.', required = True)
    parser.add_argument('--subCategory', type=str, help='Subcategory within the category.', required = False)
    parser.add_argument('--logFile', type=str, help='File into which the logs are saved', required=False, default='scraper.log')
    args = parser.parse_args()

    # Initialize logger:
    logging.basicConfig(
        filename=args.logFile,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    database_file = os.path.abspath(args.database)
    category = args.category
    startPage = args.startPage

    # URL path is changed depending if subcategory is provided or not:
    url_path = f'{category}__{args.subCategory}' if args.subCategory else category

    # One page is retrieved to determine if the category_subcategory pair is valid or not:
    test_page = download_page.download_page('{}/{}'.format(URL,url_path))

    # If the end page is not defined, we fetch the last page from the page list:
    if not args.endPage:
        endPage = parser_helper.get_last_question_page(test_page)
    else:
        endPage = args.endPage

    # Test if the endPage is higher:
    if int(startPage) >= int(endPage):
        logging.error(f'The endPage ({startPage}) must be lower than end page ({endPage})')
        raise ValueError

    # Log startup parameters:
    logging.info(f'Category: {category}')
    if args.subCategory:
        logging.info(f'Subcategory: {args.subCategory}')
    logging.info(f'First page of questions: {startPage}')
    logging.info(f'Last page of questions: {endPage}')

    ## Open database, create connection, initialize loader object:
    db_obj = db_connection.db_connection(database_file) # DB connection
    scraper_obj = scraper(db_obj)

    # Only one page is parsed if direct question is passed:
    if args.directQuestion:
        scraper_obj.get_all_questions([args.directQuestion])
        sys.exit()

    logging.info('Fetching data started...')
    
    # Looping through all defined pages:
    for page in range(startPage, endPage+1):

        # Fetch page with questions:
        question_list_page_url ='{}/{}__oldal-{}'.format(URL, url_path, page)
        soup = download_page.download_page(question_list_page_url)

        # Get URLs for all questions:
        questions = parser_helper.get_all_questions(soup)

        # Retrieve all question data:
        scraper_obj.get_all_questions(questions)

        logging.info(f'page completed: {question_list_page_url}')

    logging.info('Scarping completed.')


if __name__ == '__main__':
    
    __main__()

