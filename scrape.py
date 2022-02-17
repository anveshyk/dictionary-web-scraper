"""Extract all entries/words off Dictionary.com and store as a txt file"""

import sys
import pathlib
from typing import List, Tuple, Dict, Set, Iterator, Optional
from string import ascii_lowercase
import requests
from bs4 import BeautifulSoup

BASE_URL: str = "https://www.dictionary.com/list/"  # Dictionary.com URL


def scrape_all_words_gen() -> Iterator[str]:
    """Generator for all scraped words/phrases a to z, retaining Dictionary.com order."""

    # Scrape all words beginning with each letter
    for letter in ascii_lowercase:
        letter_url: str = BASE_URL + letter + "/"
        print(f"\nStarting letter {letter}: {letter_url}")
        pg_no: int = 1

        # Iterate through all pages
        while True:
            pg_url: str = letter_url + str(pg_no)
            page: requests.Response = requests.get(pg_url)
            if page.status_code != 200:
                break

            # Yield all words from pg with nested generator
            yield from scrape_pg_gen(page)
            pg_no += 1

        print(f"{page.status_code} status code encountered.")
        print(f"{letter}: {pg_no - 1} total pages processed.")


def scrape_pg_gen(page: requests.Response) -> Iterator[str]:
    soup: BeautifulSoup = BeautifulSoup(page.content, "html.parser")
    ul = soup.find("ul", attrs={"data-testid": "list-az-results"})  # the ul w all words inside has specific attributes
    assert ul is not None  # issue if there is no ul tag
    for li in ul.find_all("li"):
        link = li.find("a")
        if link:
            text = link.text.strip()
            yield text


def scrape_definitions() -> Dict[str, Tuple]:
    """Also scrape the word type and a list of its definitions."""
    pass


def create_all_entries_file(file_name: str):
    """All raw scraped entries"""
    output_file = pathlib.Path(file_name)
    count = 0
    with open(output_file, mode="w") as f:
        for entry in scrape_all_words_gen():
            f.write(entry + "\n")
            count += 1
    print(f"{output_file} created with {count} entries.")


def create_words_file(file_name: str):
    """Only lowercase alpha words kept, no duplicates"""
    output_file = pathlib.Path(file_name)
    with open(output_file, mode="w") as f:
        seen = set()
        for word in scrape_all_words_gen():
            if word.isalpha() and word.islower() and word not in seen:
                f.write(word + "\n")
                seen.add(word)
    print(f"{output_file} created with {len(seen)} words.")


if __name__ == "__main__":
    # Output file path should be the first and only param
    output_file = sys.argv[1]
    # create_all_entries_file(output_file)
    create_words_file(output_file)
