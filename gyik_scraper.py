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
            # Add data to db
            self.ql.add_question(data)
    def test_question(self,GYIK_ID):
        return self.ad_obj.test_question(GYIK_ID)

# def get_last_page(soup):


def get_all_questions(URL):
    soup = download_page.download_page(URL)
    questions_list = soup.findChildren('table', class_ = 'kerdes_lista')
    questions = []
    flat_questions = [item for sublist in questions_list for item in sublist]
    for td in flat_questions:
        try:
            for a in td.find_all('a'):
                url = a.get('href')
                if re.match('.+__\d+-.+', url): questions.append('https://www.gyakorikerdesek.hu' + url)
        except:
            continue 
    return questions


def __main__():
    ## Initially these variables are hardcoded:
    URL = 'https://www.gyakorikerdesek.hu'
    category = 'tudomanyok'
    database_file = '/Users/dsuveges/project/GyIK/GYIK_database.db'

    ### Open database, create connection, initialize loader object:
    db_obj = db_connection.db_connection(database_file) # DB connection

    # Get last page:
    scraper_o = scraper(db_obj)


    for page in range(500,505):
        # Fetch download page:
        question_list_page_url ='{}/{}__oldal-{}'.format(URL, category, page)
        questions = get_all_questions(question_list_page_url)
        scraper_o.get_all_questions(questions)


if __name__ == '__main__':
    __main__()