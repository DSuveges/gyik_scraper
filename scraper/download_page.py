import logging
import requests
import random

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import time
from bs4 import BeautifulSoup, UnicodeDammit

# from scraper_api import ScraperAPIClient
logger = logging.getLogger('__main__')


# Problematic questions:
## https://www.gyakorikerdesek.hu/szamitastechnika__egyeb-kerdesek__10250568-bluetooth-usb-autoradio-hogyan

# code from: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
    ):

    session = session or requests.Session()
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
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Szopj le haver. AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'})
    return session


def download_page(URL, session = None):
    '''
    This function downloads a webpage defined in the submitted URL. Given pages UTF-8 encoded, characters could be messed up.
    TODO:
        1. If empty page is retreaved, handle properly.
        2. If something wrong handle it properly.
    '''

    # Let's wait to avoid being banned (0.1 leads to ban already).
    time.sleep(10)

    # If no session is provided we generate session:
    session = requests_retry_session()

    # client = ScraperAPIClient(api_key)
    
    
    # URL to downloads:
    try:
        # response = client.get(url = URL)
        response = session.get(URL)
    except ConnectionError:
        logger.warning(f'request failed for URL: {URL}')

    # Returned html document:
    html = response.text

    # Html encoded into utf8:
    uhtml = UnicodeDammit(html)

    # Creating soup:
    soup = BeautifulSoup(uhtml.unicode_markup, features="html.parser")

    try:
        if soup.find('title').text == 'Captcha!':
            logger.warning(f"We have triggered the captcha... ({URL})")
    except AttributeError:
        raise ValueError(f'The provided URL ({URL}) cound not retrieve data. Category or subcategory might be wrong...')


    # check if the returned value contain the html.
    return soup
    
