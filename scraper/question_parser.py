# from bs4 import BeautifulSoup, UnicodeDammit
from scraper import parser_helper
import re

class parse_question(object):

    def __init__(self, soup, question_URL):
        """
        This class parses all question related data.
        The URL needs to be passed to have the GYIK ID of the question.

        :param soup: BeautifulSoup object
        :param question_URL: URL of the question. (cannot be parsed from the html page)
        """
        self.soup = soup

        # extract question:
        self.q = soup.html.body.findChild("table", class_="kerdes")

        # Parse all values:
        title = self._parse_title()
        categories = self._parse_categories()
        keywords = self._parse_keywords()
        raw_date = self._parse_date()
        user = self._parse_user()
        text = self._parse_text()
        ID_match = re.search('__(\d+?)-', question_URL)

        # Compile into some return value:
        self.question_data = {
            'URL': question_URL,
            'GYIK_ID': ID_match.group(1),
            'TITLE': title,
            'CATEGORY': categories[0],
            'SUBCATEGORY': categories[1],
            'QUESTION': text,
            'QUESTION_DATE': parser_helper.process_date(raw_date),
            'KEYWORDS': keywords,
            'USER': {'USER': user, 'USER_PERCENT': None}
        }

    def _parse_title(self):
        title = self.soup.find('div', class_='kerdes_fejlec').find('h1').text
        return title

    def _parse_categories(self):
        links = self.soup.find("div", class_="morzsamenu").findChildren('a')
        category = links[1].text
        subcategory = links[2].text

        return (category, subcategory)

    def _parse_keywords(self):
        keywords = []
        # Extracting keywords:
        try:
            for kulcsszo in self.soup.find('div', class_ = 'kerdes_kulcsszo').findAll('a'):
                keywords.append(kulcsszo.text.replace('#',''))
        except:
            return keywords

        return keywords

    def _parse_date(self):
        q_date = self.soup.find('div', title='A kérdés kiírásának időpontja')

        if q_date:
            return q_date.text
        else:
            return None

    def _parse_user(self):
        user = self.soup.find('div', class_='kerdes_fejlec')
        if len(user.findAll('div')) > 0:
            user_text = user.find('div').text
            return user_text.replace(' kérdése:', '')
        else:
            return None

    def _parse_text(self):
        kerdes_body = self.soup.find('div', class_='kerdes_kerdes')

        # Removing unwanted divs:
        for div in kerdes_body.findAll('div'):
            div.decompose()

        if kerdes_body.text:
            text = kerdes_body.text.replace('\n', ' ')
            return text
        else:
            q_text = ' '.join([x.text for x in kerdes_body.findAll('p')])
            return q_text

    def get_question_data(self):
        return self.question_data

    