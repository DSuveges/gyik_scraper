import requests
import time
from bs4 import BeautifulSoup, UnicodeDammit

# Problematic questions:
## https://www.gyakorikerdesek.hu/szamitastechnika__egyeb-kerdesek__10250568-bluetooth-usb-autoradio-hogyan

def download_page(URL):
    '''
    This function downloads a webpage defined in the submitted URL. Given pages UTF-8 encoded, characters could be messed up.
    TODO:
        1. If empty page is retreaved, handle properly.
        2. If something wrong handle it properly.
    '''

    # Let's wait to avoid being banned (0.1 leads to ban already).
    time.sleep(0.2)

    # URL to download:
    response = requests.get(URL)

    # Returned html document:
    html = response.content.decode('utf-8')

    # Html encoded into utf8:
    uhtml = UnicodeDammit(html)

    # Creating soup:
    soup = BeautifulSoup(uhtml.unicode_markup, features="html.parser")

    # check if the returned value contain the html.
    return soup
