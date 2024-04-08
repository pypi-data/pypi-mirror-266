from dataclasses import dataclass
from typing import Optional

import pydantic

@dataclass
class PatentTextLine:
    page_num: int  # 0-based index returned from PDFPageDetailedAggregator. TODO: rename to index
    text: str
    line_index: int  # line index counting TextLine instances from top to bottom of page
    column_index: Optional[int]  # 0 or 1 or None if noncolumnar
    line_num: Optional[int] = None  # human labeled line number, multiple of 5
    column_num: Optional[int] = None  # human labeled column number
    paragraph_num: Optional[int] = None  # alternative human labeling method often in form [XXXX] at beginning of paragraph

@dataclass
class GeneratedPassage:
    prior_art_source_id: int
    text: str
    claim_element_id: int
    model_id: str
    start_line: Optional[PatentTextLine] = None
    end_line: Optional[PatentTextLine] = None
    ranking: int = 0


@dataclass
class PatentUniqueID:
    patent_number: str
    country_code: str
    kind_code: Optional[str] = None

    def __repr__(self):
        return f'{self.country_code}{self.patent_number}'

    def __str__(self):
        return self.__repr__()

    @classmethod
    def from_patent_id(cls, patent_id: str):
        country_code = patent_id[:2]
        patent_number = patent_id[2:]
        return cls(patent_number=patent_number, country_code='US')

@dataclass
class GoogleClaim:
    claim_number: int
    claim_elements: list[str]


class GoogleParsedPatent(pydantic.BaseModel):
    unique_id: PatentUniqueID
    specification: Optional[str] = None
    claims: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None
    text_format: Optional[str] = None
    filing_date: Optional[str] = None
    priority_date: Optional[str] = None