from bs4 import BeautifulSoup, UnicodeDammit
from scraper import parser_helper

import re

class parse_question(object):
    
    def __init__(self, soup, question_URL):
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
            'URL' : question_URL,
            'GYIK_ID' : ID_match.group(1),
            'TITLE' : title,
            'CATEGORY' : categories[0],
            'SUBCATEGORY' : categories[1],
            'QUESTION' : text,
            'QUESTION_DATE' : parser_helper.process_date(raw_date),
            'KEYWORDS' : keywords,
            'USER' : {'USER' : user, 'USER_PERCENT' : None}
        }
        
    def _parse_title(self):
        title = self.soup.html.title.text
        return title
        
    def _parse_categories(self):
        links = self.soup.html.body.findChild("td", class_="jobb_oldal").findChildren('a')
        category = links[0].text
        subcategory = links[1].text

        return (category, subcategory)

    def _parse_keywords(self):
        small_letters = self.q.findChild('div', class_ = 'right small')
        # Extract keywords:
        if small_letters:
            kw = small_letters.find_all('a')
            return  [x.text for x in kw]
        else:
            return []

    def _parse_date(self):
        q_date = self.q.findChild('span', title='A kérdés kiírásának időpontja')

        if q_date:
            return q_date.text
        else:
            return None

    def _parse_user(self):
        user = self.q.findChild('span', class_ = 'sc0')
        if user:
            user_text = user.text
            return user_text.replace(' nevű felhasználó kérdése:', '')
        else:
            return None
        
    def _parse_text(self):
        td = self.q.findChildren('td')[2]
        
        if len(td.findChildren('p')) > 0:
            q_text = ' '.join([x.text for x in td.findChildren('p')])
        else:
            q_text = td.find(text=True, recursive=False)
            q_text = q_text.replace('\n', ' ')
        
        return q_text

    def get_question_data(self):
        return self.question_data
    
    