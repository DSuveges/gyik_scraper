from bs4 import BeautifulSoup, UnicodeDammit
from scraper import parser_helper
import re


class parse_answers(object):
    
    def __init__(self,soup):
        self.soup = soup
        
        self.answer_data = []
        
        # extracting answer table:
        answer_table = soup.html.body.findChild("table", class_="valasz")
        
        # Looping through the table and parse all questions:
        all_answers = answer_table.find_all('tr', recursive=False)
        for index, row in enumerate(all_answers):

            # Finding answer rows:
            if len(row.findChildren('td', class_ = 'valaszok vtop')) == 2:
                
                # Parsing values
                userName    = self._parse_user(row)
                answer_id   = self._parse_answer_id(row)

                # If the original poster submits a comment we don't expect percents:
                if userName == 'kerdezo_dummy_user':
                    (user_percent, answer_percent) = (None, None)
                else:
                    (user_percent, answer_percent) = self._parse_usefulness(row)

                raw_date    = self._parse_date(all_answers[index + 1])
                answer_text = self._parse_text(row)
                userName    = self._parse_user(row)
                
                # Build data structure:
                self.answer_data.append({
                    'GYIK_ID' : answer_id,
                    'USER' : {'USER' : userName, 'USER_PERCENT' : user_percent},
                    'ANSWER_DATE' : parser_helper.process_date(raw_date),
                    'ANSWER_TEXT' : answer_text,
                    'USER_PERCENT' : user_percent,
                    'ANSWER_PERCENT' : answer_percent
                })


    def _parse_answer_id(self, row):
        a_tag = row.findAll('a')

        if a_tag == 0:
            return None

        a_id = a_tag[0].get('id').replace('valasz-','')
        return a_id


    def _parse_text(self, row):
        p = row.findChildren('p')

        if len(p) > 0:
            a_text = ' '.join([x.text for x in p])
        else:
            td = row.findChildren('td')[1]
            a_text_array = td.findAll(text=True, recursive=False)
            a_text = ' '.join(a_text_array)
            a_text = a_text.replace('\n', ' ')

        if a_text.strip() == '':
            a_text_array = row.findChildren('td')[1].findAll(text=True)
            a_text_array = a_text_array[2:]
            a_text = ' '.join([x for x in a_text_array if not re.match('.+hasznos.+',x)])            
            a_text = a_text.replace('\n', ' ')

        return a_text


    def _parse_usefulness(self, row):
        u = row.findChild('div', class_ = 'right small')
        try:
            u_text = u.text
        except:
            print('[Warning] Usefulness of the answer could not be retrieved.')
            return(None, None)

        # Try to fetch usefullness of answer:
        m_a = re.search('lasz (.+?)%', u_text)

        if m_a:
            a_u = m_a.group(1)
        else:
            a_u = None

        # Try to fetch usefullness of user:
        m_u = re.search('szíró (.+?)%', u_text)

        if m_u:
            u_u = m_u.group(1)
        else:
            u_u = None    

        return (u_u, a_u)


    def _parse_date(self, row):
        date_text = row.findChild('td', class_ = 'datum').text
        return date_text


    def _parse_user(self,row):
        user = row.findChild('span', class_ = 'sc0')
        if user:
            user_name = user.text.replace(' nevű felhasználó válasza:', '')
        else:
            user_name = None

        # Assigning dummy user name for the original poster:
        if user_name == 'A kérdező kommentje:':
            user_name = 'kerdezo_dummy_user'

        return(user_name)
 

    def get_answer_data(self):
        return(self.answer_data)
 
