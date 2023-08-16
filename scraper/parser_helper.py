"""Functions to help the html parsing."""
from __future__ import annotations

import logging
import re
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING

logger = logging.getLogger("__main__")

if TYPE_CHECKING:
    from bs4 import BeautifulSoup, Tag


def get_all_questions(soup: BeautifulSoup) -> list:
    """Retrieve all question URLs on one list page.

    param:
        soup (beautifulsoup): .

    Returns:
        question_urls (list): all the links to questions.
    """

    def _parse_count(count: Tag) -> int:
        return int(count.text)

    def _parse_link(question: Tag) -> str | None:
        url = question.find("a").get("href")
        if re.match(r".+__\d+-.+", url):
            return "https://www.gyakorikerdesek.hu" + url
        else:
            return None

    def _parse_gyik_id(question: Tag) -> str | None:
        url = question.find("a").get("href")
        gyik_ids = re.search(r".+__(\d+)-.+", url)
        if gyik_ids:
            return gyik_ids[1]
        else:
            return None

    return list(
        zip(
            [
                _parse_link(tag)
                for tag in soup.findChildren("div", class_="kerdeslista_szoveg")
            ],
            [
                _parse_count(tag)
                for tag in soup.findChildren("div", class_="kerdeslista_valasz")
            ],
            [
                _parse_gyik_id(tag)
                for tag in soup.findChildren("div", class_="kerdeslista_szoveg")
            ],
        )
    )


def get_last_question_page(soup: BeautifulSoup) -> int:
    """This function returns the last page of question in a category.

    args:
        soup (BeautifulSoup) - html parsed by beautifulsoup.

    Returns:
        int - last page of the category
    """
    # Getting page numbers:
    table_footer = soup.findChildren("div", class_="oldalszamok")[1]

    # The page numbers are expected to be stored in the "oldalszamok" div:
    assert isinstance(table_footer, list) and len(table_footer) > 1

    # Extracting URLs:
    URLs = [a_tag.get("href") for a_tag in table_footer[1].findAll("a")]

    assert len(URLs) > 0, "Page numbers were failed to pull"

    return int(URLs[-1].split("-")[-1])


def get_last_answer_page(soup: BeautifulSoup) -> int | None:
    """This function returns the last page of answer for a question.

    Args:
        soup (beautifulsoup): parsed html page.

    Returns:
        number of last_page
    """
    footer = soup.findChild("td", class_="valaszok")

    if not footer:
        return None

    links = footer.findChildren("a")

    if not links:
        return None

    last_page_link = links[-1].get("href")

    return int(last_page_link.split("-")[-1])


def process_date(date_string: str) -> datetime | None:
    """Map date to standard datetime object.

    The site has a very weird data/time notation.

    Args:
        date_string (str): captured date/time annotation
    returns:
        datetime of object of the input date
    """
    # Dictionary to map Hungarian abbreviation of months to English:
    month_mapper = {
        "febr": "feb",
        "márc": "mar",
        "ápr": "apr",
        "máj": "may",
        "jún": "jun",
        "júl": "jul",
        "szept": "sep",
        "okt": "oct",
    }

    # If the date could not be parsed, a none-type is passed:
    if date_string is None:
        logger.warning(
            "[Warning] Translating date ({}) to datetime object has failed. Skipping.".format(
                date_string
            )
        )
        return None

    date_string = date_string.strip()

    # Processing unusual date annotation:
    today = date.today()  # today
    yesterday = today - timedelta(1)  # yesterday
    day_b_yesterday = today - timedelta(2)  # day before yesterday

    if "tegnapelőtt" in date_string:
        date_string = date_string.replace(
            "tegnapelőtt", day_b_yesterday.strftime("%Y. %h. %d.")
        )
    elif "tegnap" in date_string:
        date_string = date_string.replace("tegnap", yesterday.strftime("%Y. %h. %d."))
    elif "ma" in date_string:
        date_string = date_string.replace("ma", today.strftime("%Y. %h. %d."))
    else:
        for hun_month, eng_month in month_mapper.items():
            date_string = date_string.replace(hun_month, eng_month)

    # trying to translate date string to datetime object:
    try:
        date_obj = datetime.strptime(date_string, "%Y. %b. %d. %H:%M")
    except ValueError:
        date_string = "{}. {}".format(today.year, date_string)
        date_obj = datetime.strptime(date_string, "%Y. %b. %d. %H:%M")

    return date_obj
