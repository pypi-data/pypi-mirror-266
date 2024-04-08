""" Functionality to scrape and read UNESCO data from the web.


TODO: Add error handling in LinkScraper.get_links when no links are found


"""

import requests
from bs4 import BeautifulSoup
import re
from zipfile import ZipFile
import io
import pandas as pd
from functools import lru_cache

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/["
    "version] Safari/537.36"
}
BASE_URL = "https://uis.unesco.org/bdds"
MIME_TYPES = [
    "application/zip",
    "application/x-zip-compressed",
]  # multipurpose internet mail extensions types accepted


def make_request(url: str) -> requests.models.Response:
    """Make a request to a url.

    Args:
        url: url to make request to

    Returns:
        requests.models.Response: response object
    """

    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            raise ConnectionError(
                f"Could not connect to {url}. Status code: {response.status_code}"
            )
        return response
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Could not connect to {url}. Error: {str(e)}")


class UISInfoScraper:
    """Class to get data download links and other info from the unesco bulk download page."""

    @staticmethod
    def get_soup() -> BeautifulSoup:
        """Get a soup object from the UNESCO bulk download page."""

        response = make_request(BASE_URL)
        return BeautifulSoup(response.content, "html.parser")

    @staticmethod
    def parse_link_section(link_section: BeautifulSoup) -> dict | None:
        """Parse a section of the page containing a link to a zip file."""

        link = link_section.find(
            "a", href=lambda href_str: href_str.endswith(".zip")
        )  # find link with zip file

        # if no link is found to a .zip file, return None
        if link is None:
            return None

        href = link.get("href")  # get the href

        text = (
            link.find_parent().text
        )  # get the text section to find name and latest_update
        name, latest_update = UISInfoScraper.parse_link_text(text)

        return {"name": name, "latest_update": latest_update, "href": href}

    @staticmethod
    def parse_link_text(link_text: str) -> tuple:
        """Parse the link text to get the title and year of the data."""

        date_pattern = (
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+("
            r"\d{4})"
        )

        # Check if the link text contains a date
        match = re.search(date_pattern, link_text)

        # If a date is found, extract the name and the date
        if match:
            name = link_text[: match.start()]
            latest_update = match.group()
        # If no date is found, return latest_update as None
        else:
            name = link_text
            latest_update = None

        other_text_pattern = (
            r"\s*[\-\(\):]*\s*last update\s*[\-\(\):]*\s*"  # to remove "last update"
        )
        name = re.sub(other_text_pattern, "", name).strip(
            "(- "
        )  # remove unwanted text from name

        return name, latest_update

    @staticmethod
    def get_links() -> list[dict]:
        """Get a list of dictionaries containing the theme, name, latest update, and href of each zip file.

        Returns:
            list of dictionaries containing the theme, name, latest update, and href of each zip file
        """

        links_list = []
        soup = UISInfoScraper.get_soup()

        # loop through each theme section
        for theme in soup.find_all("h2"):
            theme_name = theme.text
            section = theme.find_parent(
                "section"
            )  # get the section containing the theme

            # loop through each link section in the theme section
            for link_section in section.find_all("li"):
                parsed_links_dict = UISInfoScraper.parse_link_section(link_section)
                if parsed_links_dict is not None:
                    parsed_links_dict.update({"theme": theme_name})
                    links_list.append(parsed_links_dict)

        return links_list


def get_zipfile(url: str) -> ZipFile:
    """Extract a zipfile from a url and return a ZipFile object.

    Args:
        url: url to the zipfile

    Returns:
        ZipFile: ZipFile object containing the zipfile
    """

    response = make_request(url)

    # check that response is a zip file
    if not response.headers["Content-Type"] in MIME_TYPES:
        raise ValueError("The file is not an accepted zip file")

    return ZipFile(io.BytesIO(response.content))


def read_csv(zipfile: ZipFile, path: str) -> pd.DataFrame:
    """Read a CSV file from a ZipFile object.

    Args:
        zipfile: ZipFile object containing the CSV file
        path: path to the CVS in the zipped folder

    Returns:
        pd.DataFrame: dataframe containing the data from the CSV
    """

    if path not in zipfile.namelist():
        raise FileNotFoundError(f"Could not find file: {path}")

    return pd.read_csv(zipfile.open(path), low_memory=False)


def read_md(zipfile: ZipFile, path: str) -> str:
    """Read a Markdown file from a ZipFile object.

    Args:
        zipfile: ZipFile object containing the Markdown file
        path: path to the Markdown file in the zipped folder

    Returns:
        str: string containing the Markdown text
    """

    if path not in zipfile.namelist():
        raise FileNotFoundError(f"Could not find file: {path}")

    with zipfile.open(path) as md_file:
        # Read and decode the content of the .md file
        content = md_file.read().decode("utf-8")

    return content
