from scraper import download_page
from scraper import question_retriever
from scraper import parser_helper

from db_tools import db_connection
from db_tools import add_data

import argparse
import re


class scraper(object):
    def __init__(self, db_obj):
        self.ad_obj = add_data.data_loader(db_obj.conn) # 
        self.ql = add_data.question_loader(self.ad_obj) # Question loader
    
    def get_all_questions(self, URL_list):
        for URL in URL_list:
            match = re.search('__(\d+)-',URL)
            if self.test_question(match[1]): continue
            rq = question_retriever.retrieve_question(URL)
            data = rq.get_data()
            self.ql.add_question(data)
    def test_question(self,GYIK_ID):
        return self.ad_obj.test_question(GYIK_ID)



def __main__():
    """
    The main function of the GYIK scraper application.
    User can specify the category, start page, end page and the database file into which
    the data is saved.
    """

    # Core URL:
    URL = 'https://www.gyakorikerdesek.hu'

    parser = argparse.ArgumentParser()
    parser.add_argument('--category', type=str, help='Main category. Mandatory', required = True)
    parser.add_argument('--startpage', type=int, help='Start page of the question list', required = False, default = 0)
    parser.add_argument('--endpage', type=int, help='end page of the question list.', required = False)
    parser.add_argument('--database', type=str, help='Email address where the notification is sent.', required = True)
    args = parser.parse_args()

    database_file = args.database
    category = args.category
    startpage = args.startpage

    # If the end page is not defined, we fetch the last page from the page list:
    if not args.endpage:
        print('[Info] End page is not defined. Fetching last page of the category ({}).'.format(category))
        soup = download_page.download_page('{}/{}'.format(URL,category))

        # There's an attribute error if the category is not properly typed:
        try:
            endpage = parser_helper.get_last_question_page(soup)
        except AttributeError:
            print('[Error] Cound not find page for category: {}'.format(category))
            raise
    else:
        endpage = args.endpage

    # Test if the endpage is higher:
    if int(startpage) >= int(endpage):
        print('[Error] The endpage ({}) must be lower than end page ({})'.format(startpage, endpage))
        raise ValueError

    print('[Info] Category: {}'.format(category))
    print('[Info] First page of questions: {}'.format(startpage))
    print('[Info] Last page of questions: {}'.format(endpage))

    ## Open database, create connection, initialize loader object:
    db_obj = db_connection.db_connection(database_file) # DB connection
    scraper_o = scraper(db_obj)

    for page in range(startpage,endpage):
        # Fetch download page:
        question_list_page_url ='{}/{}__oldal-{}'.format(URL, category, page)
        print(question_list_page_url)
        soup = download_page.download_page(question_list_page_url)

        # Get question URLs:
        questions = parser_helper.get_all_questions(soup)
        
        # Retrieve all question data:
        scraper_o.get_all_questions(questions)


if __name__ == '__main__':
    __main__()