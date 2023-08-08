import logging

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import time
from bs4 import BeautifulSoup, UnicodeDammit

from faker import Faker

# from scraper_api import ScraperAPIClient # If using scraperAPI
logger = logging.getLogger('__main__')

# Using a random user agent all the time
faker = Faker()

# code from: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
    ):

    session = Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update({'User-Agent': faker.user_agent()})
    return session


def download_page(URL, session=None):
    '''This function downloads a webpage defined in the submitted URL.

    Given pages UTF-8 encoded, characters could be messed up.
    TODO:
        1. If empty page is retreaved, handle properly.
        2. If something wrong handle it properly.
    '''

    # Let's wait to avoid being banned (0.1 leads to ban already).
    time.sleep(3)

    while True:
        try:
            # If no session is provided we generate session:
            session = requests_retry_session()

            # URL to downloads:
            try:
                # response = client.get(url = URL) # If using screapAPI
                response = session.get(URL)
            except ConnectionError:
                logger.warning(f'request failed for URL: {URL}')

            # Returned html document:
            html = response.text.encode('utf-8', 'replace').decode()

            # Html encoded into utf8:
            uhtml = UnicodeDammit(html)

            # Creating soup:
            soup = BeautifulSoup(uhtml.unicode_markup, features="html.parser")

            # If certain protection mechanism is triggered we won't return anything:
            if soup.find('title').text == 'Captcha!':
                logger.warning(f"We have triggered the captcha... ({URL})")
                raise ValueError(f'While fetching URL ({URL}) captcha was triggered. Exiting.')
            elif soup.find('title').text == 'Ideiglenes letiltás!':
                logger.warning(f'We are termporarily banned to access any page.')
                raise ValueError(f'While fetching URL ({URL}) we got banned termporarily. Exiting.')

            # Upon successful retrieval, we are breaking out the while loop and return the page:
            return soup

        except:
            # After the failed attempt the script waits 30 seconds and try again:
            time.sleep(30)
            continue
