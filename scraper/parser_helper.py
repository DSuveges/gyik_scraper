from bs4 import BeautifulSoup, UnicodeDammit
import datetime


def get_last_page(soup):
    footer = soup.findChild('td', class_ = 'valaszok')

    if not footer: return None 
        
    links = footer.findChildren('a')

    if not links: return None
        
    last_page_link = links[-1].get('href')
    
    return int(last_page_link.split('-')[-1])
    
def process_date(date_string):
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
    
    # Strip whitespace:
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
    except:
        date_string = '{}. {}'.format(today.year, date_string)
        date_obj = datetime.datetime.strptime(date_string, '%Y. %b. %d. %H:%M')
        
    return date_obj  

