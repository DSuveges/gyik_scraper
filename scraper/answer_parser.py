from scraper import parser_helper
import re


class parse_answers(object):

    def __init__(self, soup):
        """
        This class parses all answer related data.

        :param soup: BeautifulSoup object
        """

        self.soup = soup
        self.answer_data = []

        # Looping through the table and parse all questions:
        for answer in self.soup.findAll('div', id=lambda x: x and x.startswith('valasz-')):

            # Extract answer id:
            answer_id = answer.get('id').split('-')[1]

            # Parsing user name if available:
            userName = self._parse_user(answer)

            # If the original poster submits a comment we don't expect usefulness values:
            if userName == 'kerdezo_dummy_user':
                (user_percent, answer_percent) = (None, None)
            else:
                (user_percent, answer_percent) = self._parse_usefulness(answer)

            # Parse date and time of providing answer:
            answer_date = self._parse_date(answer)

            # Parsing answer text:
            answer_text = self._parse_text(answer, answer_id)

            # Removing links:
            answer_text = answer_text.replace('[link]', '')

            # Build data structure:
            self.answer_data.append({
                'GYIK_ID' : int(answer_id),
                'USER' : {'USER' : userName, 'USER_PERCENT' : user_percent},
                'ANSWER_DATE' : parser_helper.process_date(answer_date),
                'ANSWER_TEXT' : answer_text,
                'USER_PERCENT' : user_percent,
                'ANSWER_PERCENT' : answer_percent
            })

        # Parsing last page:
        self.next_page = self.find_next_page()


    @staticmethod
    def _parse_text(row, answer_id):
        answer_body = row.find('div', id=f'valasz{answer_id}')

        # Looping through all divs and delete them:
        for div in answer_body.findAll('div'):
            div.decompose()

        return answer_body.text


    @staticmethod
    def _parse_usefulness(row):

        # Get answer header:
        header = row.find('div', class_=lambda x: x and x.endswith('_fejlec'))
        stars = header.find('span', class_='vsz')

        # Parsing user usefulness:
        try:
            user_usefullness = 0
            for star in stars.findAll('img'):
                link = star.get('src')
                match = re.search('vsz(\d)\.png', link)
                user_usefullness += 10 * int(match.group(1))
        except:
            user_usefullness = None

        # Parsing answer usefulness:
        try:
            text = row.find('text', x=50).text
            answer_usefullness = int(text.replace('%',''))
        except AttributeError:
            # This happens for answers with not enough rating:
            answer_usefullness = None

        return (user_usefullness, answer_usefullness)


    @staticmethod
    def _parse_date(row):
        footer = row.find('div', class_ = lambda x: x and x.endswith('_statusz')).findAll('div')
        return footer[0].text


    @staticmethod
    def _parse_user(row):

        header_text = row.find('div', class_=lambda x: x and x.endswith('_fejlec')).text
        match =  re.search('\d+/\d+(.+)válasza', header_text)

        try:
            user_name = match.group(1).strip()
        except:
            user_name = 'kerdezo_dummy_user'

        # Anonim users are ignored:
        if user_name == 'anonim':
            user_name = None

        return user_name


    def get_next_page(self):
        return(self.next_page)


    def find_next_page(self):
        """
        Returns an url or None depending if the the page has a next page link:
        """
        try:
            pages = self.soup.find('div', class_='oldalszamok')
            lastpage_url = pages.find('a', string="❯").get('href')
            return f'https://www.gyakorikerdesek.hu{lastpage_url}'

        except:
            return None



    def get_answer_data(self):
        return(self.answer_data)

