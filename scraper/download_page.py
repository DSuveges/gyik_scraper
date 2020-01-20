import requests
import time 
from bs4 import BeautifulSoup, UnicodeDammit

def download_page(URL):
    '''
    This function downloads a webpage defined in the submitted URL.
    
    Do some trouble shooting: restart download if the first attempt was unsuccessful, returned data read into a bs object.
    '''
    
    # Let's wait
    time.sleep(0.1)
    
    # URL to download:
    response = requests.get(URL)

    # Returned html document:
    html = response.content

    # Html encoded into utf8:
    uhtml = UnicodeDammit(html)

    # Creating soup:
    soup = BeautifulSoup(uhtml.unicode_markup, features="html.parser")
    
    # check if the returned value contain the html.
    return soup
