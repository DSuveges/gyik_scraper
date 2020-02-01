import logging
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import time
from bs4 import BeautifulSoup, UnicodeDammit

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
    return session


def download_page(URL, session = None):
    '''
    This function downloads a webpage defined in the submitted URL. Given pages UTF-8 encoded, characters could be messed up.
    TODO:
        1. If empty page is retreaved, handle properly.
        2. If something wrong handle it properly.
    '''

    # Let's wait to avoid being banned (0.1 leads to ban already).
    time.sleep(0.2)

    # If no session is provided we generate session:
    if not session:
        session = requests_retry_session()

    response = session.get(URL,timeout=5)

    # URL to download:
    try:
        response = requests.get(URL)
    except ConnectionError:
        print('[Warning] Problem with connection. After 1 sec. retrying.')
        time.sleep(1)
        response = requests.get(URL)

    # Returned html document:
    html = response.content.decode('utf-8')

    # Html encoded into utf8:
    uhtml = UnicodeDammit(html)

    # Creating soup:
    soup = BeautifulSoup(uhtml.unicode_markup, features="html.parser")

    # check if the returned value contain the html.
    return soup
