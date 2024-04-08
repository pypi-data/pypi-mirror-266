import requests
import pathlib
import time
import typing
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from functools import cached_property
from logging import getLogger

from langchain.text_splitter import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup

from patent_chart.data_structures import GoogleParsedPatent, PatentUniqueID, GoogleClaim

logger = getLogger(__name__)


class GoogleParseError(Exception):
    pass


def google_request_with_retry(url, max_retries=3):
    for i in range(1, max_retries + 1):
        response = requests.get(url)
        if response.status_code == 200:
            return response
        else:
            logger.warning('Failed to request %s. Response code: %s. Error: %s', url, response.status_code, response.text)
            logger.warning('Retrying %s', url)
            time.sleep(i**2)
    return None

def parse_google_claims(claims:str) -> list[GoogleClaim]:
    # Trim beginning of claims
    claim_begin = claims.find('1.')

    trimmed_claims = claims[claim_begin:]
    claim_lines = [l.strip() for l in trimmed_claims.split('\n') if l.strip()]

    claim_number = 1
    google_claims = []
    claim = GoogleClaim(
        claim_number=claim_number,
        claim_elements=[]
    )
    for line in claim_lines:
        if line.startswith(str(claim_number + 1)):
            claim_number += 1
            google_claims.append(claim)
            claim = GoogleClaim(
                claim_number=claim_number,
                claim_elements=[]
            )
        claim.claim_elements.append(line)

    return google_claims


filing_date_regex = re.compile(r'filing|filed')


class GooglePatent:
    def __init__(self, patent_id, html_text=None) -> None:
        self.patent_id = patent_id
        if html_text is None:
            self.soup = BeautifulSoup(requests.get(f"https://us-west1-careful-ai.cloudfunctions.net/google-patents?patent_id={patent_id}").text, 'html.parser')
        else:
            self.soup = BeautifulSoup(html_text, 'html.parser')
    
    @classmethod
    def from_html_text(cls, patent_id, html_text):
        return cls(patent_id, html_text)

    def _get_index_of_priority_date(self, table) -> int:
        if table:
            for index, span in enumerate(table.find("div", class_="thead").find_all("span", class_="th")):
                if span.get_text().strip().lower() == "priority date":
                    return index
        return -1

    def _extract_priority_dates(self, table):
        dates = []
        if table:
            for row in table.find("div", class_="tbody").find_all("div", class_="tr"):
                date_string = row.find_all("span")[self._get_index_of_priority_date(table)].get_text().strip()
                dates.append(datetime.strptime(date_string, "%Y-%m-%d"))
        return dates

    def _extract_priority_dates_from_parent_apps(self):
        if self.soup.find("h3", id="parentApplications"):
            if self.soup.find("h3", id="parentApplications").find_next_sibling():
                table = self.soup.find("h3", id="parentApplications").find_next_sibling().find("div", class_="table")
                return self._extract_priority_dates(table)
        return []
    
    def _extract_priority_dates_from_child_apps(self):
        if self.soup.find("h3", id="applicationChildApps"):
            if self.soup.find("h3", id="applicationPriorityApps").find_next_sibling():
                table = self.soup.find("h3", id="applicationPriorityApps").find_next_sibling().find("div", class_="table")
            return self._extract_priority_dates(table)
        return []

    def _extract_priority_dates_from_priority_apps(self):
        if self.soup.find("h3", id="applicationPriorityApps"):
            if self.soup.find("h3", id="applicationPriorityApps").find_next_sibling():
                table = self.soup.find("h3", id="applicationPriorityApps").find_next_sibling().find("div", class_="table")
            return self._extract_priority_dates(table)
        return []
    
    @cached_property
    def filing_date(self) -> datetime:
        application_timeline = self.soup.find('application-timeline')
        if not application_timeline:
            return None
        filing_date = application_timeline.find('div', class_=filing_date_regex)
        if filing_date:
            return datetime.strptime(filing_date.text, "%Y-%m-%d")
        return None

    @cached_property
    def inferred_priority_date(self):
        # TODO: figure out validation w/ prior art link
        # TODO: add child patents
        dates = self._extract_priority_dates_from_parent_apps() + self._extract_priority_dates_from_child_apps() + self._extract_priority_dates_from_priority_apps()
        if dates:
            # TODO: validate this logic - maybe take earliest one
            return min(dates)
        return None

    @cached_property
    def pdf_url(self) -> str:
        for a in self.soup.find_all("a"):
            if a.get_text().strip() == "Download PDF":
                return a.attrs["href"]
        return None

    @cached_property
    def prior_art_url(self) -> str:
        for a in self.soup.find_all("a"):
            if a.get_text().strip() == "Find Prior Art":
                if a.attrs["href"] != "#":
                    return a.attrs["href"]
        return None
    
    @cached_property
    def abstract(self) -> str:
        return self.soup.find("div", class_="abstract").get_text().strip() if self.soup.find("div", class_="abstract") else None

    @cached_property
    def title(self) -> str:
        return self.soup.find("h1", id="title").get_text().strip() if self.soup.find("h1", id="title") else None

    @cached_property
    def specification(self) -> str:
        return str(self.soup.find('section', id='description')) if self.soup.find('section', id='description') else None

    @cached_property
    def specification_text(self) -> str:
        specification = self.soup.find('section', id='description')
        return specification.get_text() if specification else None

    @cached_property
    def claims(self) -> str:
        return str(self.soup.find('section', id='claims')) if self.soup.find('section', id='claims') else None

    @cached_property
    def claims_text(self) -> str:
        claims = self.soup.find('section', id='claims')
        return claims.get_text() if claims else None

    @cached_property
    def jurisdiction(self) -> str:
        if self.soup.find("section", class_="knowledge-card"):
            if self.soup.find("section", class_="knowledge-card").find("header"):
                if self.soup.find("section", class_="knowledge-card").find("header").find("p"):
                    return self.soup.find("section", class_="knowledge-card").find("header").find("p").get_text().strip()
        return None
    
    @cached_property
    def known_references(self) -> list[str]:
        header = self.soup.find('h3', id='patentCitations')
        table = header.find_next_sibling()
        return [a.text for a in table.find_all('a')]


def parse_google_patent(patent_unique_id: PatentUniqueID) ->  GoogleParsedPatent | None:
    # Uses selenium to get dates -- probably faster way but whatever
    patent = GooglePatent(patent_unique_id)

    return GoogleParsedPatent(
        unique_id=patent_unique_id,
        specification=patent.specification_text,
        claims=patent.claims_text,
        title=patent.title,
        text=str(patent.soup),
        text_format='google_html_with_selenium',
        filing_date=patent.filing_date.strftime('%Y-%m-%d'),
        priority_date=patent.inferred_priority_date.strftime('%Y-%m-%d'),
    )


def extract_text_recursive(element: ET.Element):
    text = ''
    if element.text:
        text += element.text
    for child in element:
        text += extract_text_recursive(child)
    if element.tail:
        text += element.tail
    return text


def chunk_written_description_with_pos(description: ET.Element, chunk_size_words=8191, chunk_overlap_words=1024) -> tuple[list[str], list[tuple[int]]]:
    text = ''
    for elem in description:
        if elem.tag not in ['p', 'heading']:
            elem_text = ' '.join([extract_text_recursive(child) for child in elem])
        else:
            elem_text = extract_text_recursive(elem)
        text += elem_text
        if elem.tag == 'p':
            text += '\n'

    return chunk_written_description_from_text_with_pos(text, chunk_size_words, chunk_overlap_words)


def chunk_written_description_from_text_with_pos(text: str, chunk_size_words=8191, chunk_overlap_words=1024) -> tuple[list[str], list[tuple[int]]]:
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name='gpt-4',
        chunk_size=chunk_size_words,
        chunk_overlap=chunk_overlap_words,
    )

    chunks = text_splitter.split_text(text)

    # Find start and end char pos for each chunk
    pos = 0
    starts = []
    ends = []
    for chunk in chunks:
        starts.append(pos)
        pos += len(chunk)
        ends.append(pos)

    return chunks, list(zip(starts, ends))


def extract_chunked_claims_and_spec(patent: GoogleParsedPatent):
    claims = patent.claims
    specification = patent.specification
    google_claims = parse_google_claims(claims.strip(' \n'))
    claims = ['\n'.join(claim.claim_elements) for claim in google_claims]
    specification = specification.strip(' \n')
    specification_chunks_with_pos = chunk_written_description_from_text_with_pos(specification)
    return claims, specification_chunks_with_pos


# Deprecated, but keeping for reference
# def parse_google_patent(patent_unique_id: PatentUniqueID) ->  GoogleParsedPatent | None:
#     url = f"https://patents.google.com/patent/{patent_unique_id}/en"

#     logger.info('Requesting %s', url)

#     # Send an HTTP GET request to fetch the webpage
#     response = google_request_with_retry(url)

#     # Parse the HTML content of the page using BeautifulSoup
#     soup = BeautifulSoup(response.text, 'html.parser')

#     specification = soup.find('section', {'itemprop': 'description'})
#     claims = soup.find('section', {'itemprop': 'claims'})
    

#     if specification is None or claims is None:
#         logger.warning('Failed to parse %s', url)
#         return None

#     title = soup.find('td', {'itemprop': 'title'})
    
#     title_text = None
#     if title is not None:
#         title_text = title.text.strip(' \n')

#     text = str(soup)
#     text_format = 'google_html'

#     return GoogleParsedPatent(
#         unique_id=patent_unique_id,
#         title=title_text,
#         text=text,
#         text_format=text_format,
#     )

# if __name__ == '__main__':
#     package_dir = pathlib.Path(__file__).parents[1]
#     us_patents_dir = package_dir / 'us_patents_1980-2020'
#     for pdf_path in us_patents_dir.glob('*.pdf'):
#         unique_id = parser.parse_patent_unique_id_from_pdf_path(pdf_path)
#         if unique_id is not None:
#             google_unique_id = f'{unique_id.country_code}{unique_id.patent_number}{unique_id.kind_code or ""}'
#             result = parse_google_patent(google_unique_id)
#             if result is not None:
#                 specification, claims = result
#                 assert specification != ''
#                 assert claims != ''
#             else:
#                 print(f'Failed to parse {unique_id}')
#         else:
#             print(f'Failed to parse {pdf_path}')