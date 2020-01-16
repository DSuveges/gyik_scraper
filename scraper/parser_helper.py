from bs4 import BeautifulSoup, UnicodeDammit


def get_last_page(soup):
    footer = soup.findChild('td', class_ = 'valaszok')

    if not footer: return None 
        
    links = footer.findChildren('a')

    if not links: return None
        
    last_page_link = links[-1].get('href')
    
    return int(last_page_link.split('-')[-1])
    
