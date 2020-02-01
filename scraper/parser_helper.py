# from bs4 import BeautifulSoup, UnicodeDammit
import datetime
import re

"""
In this module there are a series of functions to help the parsing process.
"""


def get_all_questions(soup):
    """
    This function retrieves all question URLs on one list page.

    param: soup - beautifulsoup boject.
    Returns: question_urls (list): all the links to questions.
    """
    questions_list = soup.findChildren('table', class_ = 'kerdes_lista')
    questions = []
    flat_questions = [item for sublist in questions_list for item in sublist]
    for td in flat_questions:
        try:
            for a in td.find_all('a'):
                url = a.get('href')
                if re.match('.+__\d+-.+', url): questions.append('https://www.gyakorikerdesek.hu' + url)
        except AttributeError:
            # All answers on one page
            continue
    return questions


def get_last_question_page(soup):
    """
    This function returns the last page of question in a category

    param: soup - beautifulsoup boject.
    Returns: last_page (int)
    """
    full_table = soup.findChild('td', class_ = 'kismenu_main')
    table_footer = full_table.findChildren('div', class_='center')[1]
    URLs = [a_tag.get('href') for a_tag in table_footer.findAll('a') ]
    if len(URLs) == 0:
        print('[Warning] Failed to retrieve last page.')
        return None
    last_page = URLs[-1].split('-')[-1]
    return last_page


def get_last_answer_page(soup):
    """
    This function returns the last page of answer for a question

    param: soup - beautifulsoup boject.
    Returns: last_page (int)
    """
    footer = soup.findChild('td', class_ = 'valaszok')

    if not footer: return None

    links = footer.findChildren('a')

    if not links: return None

    last_page_link = links[-1].get('href')

    return int(last_page_link.split('-')[-1])


def process_date(date_string):
    """
    The site has a very weird data/time notation. This function maps it to
    standard datetime object.

    param: string
    returns: datetime of object of the input date
    """

    # Dictionary to map Hungarian abbreviation of months to English:
    month_mapper = {
        'febr' : 'feb',
        'márc' : 'mar',
        'ápr'  : 'apr',
        'máj'  : 'may',
        'jún'  : 'jun',
        'júl'  : 'jul',
        'szept': 'sep',
        'okt'  : 'oct'
    }

    # If the date could not be parsed, a none-type is passed:
    if date_string is None:
        print('[Warning] Translating date ({}) to datetime object has failed. Skipping.'.format(date_string))
        return None

    date_string = date_string.strip()

    # Processing unusual date annotation:
    today = datetime.date.today() # today
    yesterday = today - datetime.timedelta(1) # yesterday
    day_b_yesterday = today - datetime.timedelta(2) # day before yesterday

    if 'tegnapelőtt' in date_string:
        date_string = date_string.replace('tegnapelőtt', day_b_yesterday.strftime('%Y. %h. %d.'))
    elif 'tegnap' in date_string:
        date_string = date_string.replace('tegnap', yesterday.strftime('%Y. %h. %d.'))
    elif 'ma' in date_string:
        date_string = date_string.replace('ma', today.strftime('%Y. %h. %d.'))
    else:
        for hun_month, eng_month in month_mapper.items():
            date_string = date_string.replace(hun_month, eng_month)

    # trying to translate date string to datetime object:
    try:
        date_obj = datetime.datetime.strptime(date_string, '%Y. %b. %d. %H:%M')
    except ValueError:
        date_string = '{}. {}'.format(today.year, date_string)
        date_obj = datetime.datetime.strptime(date_string, '%Y. %b. %d. %H:%M')

    return date_obj

