from scraper import parser_helper
import re


class parse_answers(object):

    def __init__(self,soup):
        """
        This class parses all answer related data.

        :param soup: BeautifulSoup object
        """

        self.soup = soup
        self.answer_data = []

        # Looping through the table and parse all questions:
        for answer in self.soup.findAll('div', id=lambda x: x and x.startswith('valasz-')):

            print(answer.attrs)
            print(answer.get('id'))

            # Extract answer id:
            answer_id = answer.get('id').split('-')[1]

            # Extract user name:
            header_text = answer.find('div', class_='valasz_fejlec').text
            
            match =  re.search('\d+/\d+(.+)válasza', header_text)
            if match:
                print(header_text)
                print(match.group(1))
            continue

            # Extract text:


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
                    'GYIK_ID' : int(answer_id),
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
        usefullness = row.findChild('div', class_ = 'right small')
        try:
            usefullness_text = usefullness.text
        except AttributeError:
            # This happens for answers with no usefulness available for users and answers
            return(None, None)

        # Try to fetch usefullness of answer:
        match_answer = re.search('lasz (.+?)%', usefullness_text)

        if match_answer:
            answer_usefullness = match_answer.group(1)
        else:
            answer_usefullness = None

        # Try to fetch usefullness of user:
        match_user = re.search('szíró (.+?)%', usefullness_text)

        if match_user:
            user_usefullness = match_user.group(1)
        else:
            user_usefullness = None

        return (user_usefullness, answer_usefullness)


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

