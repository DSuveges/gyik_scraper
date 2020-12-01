# from bs4 import BeautifulSoup, UnicodeDammit
from scraper import download_page
from scraper import question_parser
from scraper import answer_parser
from scraper import parser_helper

class retrieve_question(object):

    def __init__(self, URL):
        self.soup = self.fetch_url(URL)
        self.url = URL

        # Parse question data:
        pq = question_parser.parse_question(self.soup, URL)

        # Parsing question related information:
        self.question_document = pq.get_question_data()

        # if we know who asked the question:
        self.user = self.question_document['USER']['USER']

        # Parsing answers:
        self.question_document['ANSWERS'] = self.parse_answers()

        
    def get_data(self):
        return self.question_document


    def parse_answers(self, url=None):

        # if url is given, the url is fetch, otherwise we use the original html:
        if url:
            soup = self.fetch_url(url)
        else:
            soup = self.soup

        # Parse answers:
        pa = answer_parser.parse_answers(soup)
        answers = pa.get_answer_data()

        # if we know who asked the question update with the name:
        if self.user:
            for answer in answers:
                if answer['USER']['USER'] == 'kerdezo_dummy_user':
                    answer['USER']['USER'] = self.user

        # If there's a next page, go there:
        if pa.get_next_page():
            answers += self.parse_answers(pa.get_next_page())

        return answers


    @staticmethod
    def fetch_url(url):
       return download_page.download_page(url) 

