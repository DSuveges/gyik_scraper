from bs4 import BeautifulSoup, UnicodeDammit

class retrieve_question(object):

    def __init__(self, URL):
        soup = download_page(URL)

        # Parse question data:
        pq = parse_question(soup, URL)

        # Initialize document:
        question_document = pq.get_question_data()
        question_document['ANSWERS'] = []

        # Parse answer data on first page:
        pa = parse_answers(soup)
        if pa.get_answer_data():
            question_document['ANSWERS'] += pa.get_answer_data()

        # Get last page:
        last_page = get_last_page(soup)

        if last_page:
            for page_URL in ['{}__oldal-{}'.format(URL,x) for x in range(1,last_page+1)]:
                print('.', sep='')
                soup = download_page(page_URL)
                pa = parse_answers(soup)

                question_document['ANSWERS'] += pa.get_answer_data()

        self.question_document = question_document
        
    def get_data(self):
        return self.question_document

