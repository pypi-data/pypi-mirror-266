import re
import pathlib
import copy
from enum import Enum
from dataclasses import dataclass
from typing import IO, Optional, BinaryIO
from collections import namedtuple
from logging import getLogger

import pydantic
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTPage, LTChar, LTAnno, LAParams, LTTextBox, LTTextLine, LTContainer
from pdfminer.pdfpage import PDFPage

from patent_chart.google_patents import parse_google_patent
from patent_chart.data_structures import PatentTextLine, PatentUniqueID, GoogleParsedPatent, GoogleClaim

logger = getLogger(__name__)

StrBytePath = str | IO | pathlib.Path

claim_number_regex = re.compile(r'\s*\d{1,2}\.')

class TokenType(Enum):
    DELIMITER_START_CLAIM = 'DELIMITER_START_CLAIM'
    # DELIMITER_END_CLAIM = 'DELIMITER_END_CLAIM'
    DELIMITER_END_PREAMBLE = 'DELIMITER_END_PREAMBLE'
    DELIMITER_END_ELEMENT = 'DELIMITER_END_ELEMENT'
    TEXT = 'TEXT'
    WHITESPACE = 'WHITESPACE'
    DEPENDENCY = 'DEPENDENCY'

@dataclass
class Token:
    type: TokenType
    lexeme: str

class ClaimsLexer(Enum):
    # TODO: move start claims section into here instead of as a pre-processing step. That way we can just run this on the whole patent rather than pre-processing the claims first. If we do that, also uncomment the end claims section delimiter.
    # DELIMITER_END_CLAIMS_SECTION = re.compile(r'k k k k k')
    DELIMITER_START_CLAIM = re.compile(r'[1-9][0-9]*\s*\.')
    # TODO: handle multiple dependency, which would include language like:
    #   claim 3 or 4
    #   claim 1 or claim 2
    #   claim 1, 7, 12, or 15
    #   claim 1, claim 7, claim 12, or claim 15
    #   any of the preceding claims
    DEPENDENCY = re.compile(r'[Cc]laim [1-9][0-9]*')
    DELIMITER_END_PREAMBLE = re.compile(r':')
    DELIMITER_END_ELEMENT = re.compile(r';')
    # DELIMITER_END_CLAIM = re.compile(r'\.')
    # TODO: add transition type:
    #   comprising
    #   consisting of
    #   consisting essentially of
    #   etc...
    # TEXT = re.compile(r'[\w,\'\"!?\(\)\-—/]+')
    TEXT = re.compile(r'[\w,\'\"!?\(\)\-—/\.]+')  # Text including period
    WHITESPACE = re.compile(r'\s+')

    def __repr__(self):
        return self.name
    
class LexicalError(Exception):
    pass

class ParseError(Exception):
    pass

def lex_claims(claim_text):
    tokens = []
    while claim_text:
        token_matched = False
        for token_type in ClaimsLexer:
            match = token_type.value.match(claim_text)
            if match:
                token_matched = True
                tokens.append(Token(getattr(TokenType, token_type.name), lexeme=match.group()))
                claim_text = claim_text[match.end():]
                break
        if not token_matched:
            raise LexicalError(f'No token matched for claim text: {claim_text[:10]}')
    return tokens

# Base recursive descent parser
class RecursiveDescentParserBase:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        
    def peek(self):
        return self.tokens[self.current_token_index]
    
    def is_at_end(self):
        return self.current_token_index == len(self.tokens)
    
    def previous(self):
        return self.tokens[self.current_token_index - 1]

    def advance(self):
        self.current_token_index += 1
        return self.previous()

    def reverse(self):
        self.current_token_index -= 1
        return self.previous()

    def check(self, type):
        if self.is_at_end():
            return False
        return type == self.peek().type

    def match(self, *token_types):
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def consume(self, token_type):
        if self.match(token_type):
            return self.previous()
        else:
            raise Exception(f'Expected {token_type.name}')

    def parse(self):
        pass

# Define dataclasses for concrete syntax tree for claims parser
# NOTE: order of definition matters for pydantic validation
@dataclass
class ClaimText:
    text: Token

@dataclass
class ClaimDelimiterEndPreamble:
    delimiter_end_preamble: Token

@dataclass
class ClaimDelimiterEndElement:
    delimiter_end_element: Token

@dataclass
class ClaimWhitespace:
    whitespace: Token

@dataclass
class ClaimDependency:
    dependency: Token

# @dataclass
# class Claim:
#     delimiter_start_claim: Token
#     claim_content: list[ClaimText | ClaimDelimiterEndPreamble |ClaimDelimiterEndElement | ClaimWhitespace | ClaimDependency]
#     delimiter_end_claim: Token


@dataclass
class Claim:
    delimiter_start_claim: Token
    claim_content: list[ClaimText | ClaimDelimiterEndPreamble |ClaimDelimiterEndElement | ClaimWhitespace | ClaimDependency]

@dataclass
class Claims:
    claims: list[Claim]

class ClaimsParser(RecursiveDescentParserBase):
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0

    def claim_content(self):
        if self.match(TokenType.TEXT):
            text = self.previous()
            return ClaimText(text=text)
        elif self.match(TokenType.WHITESPACE):
            whitespace = self.previous()
            return ClaimWhitespace(whitespace=whitespace)
        elif self.match(TokenType.DEPENDENCY):
            dependency = self.previous()
            return ClaimDependency(dependency=dependency)
        elif self.match(TokenType.DELIMITER_END_PREAMBLE):
            delimiter_end_preamble = self.previous()
            return ClaimDelimiterEndPreamble(delimiter_end_preamble=delimiter_end_preamble)
        elif self.match(TokenType.DELIMITER_END_ELEMENT):
            delimiter_end_element = self.previous()
            return ClaimDelimiterEndElement(delimiter_end_element=delimiter_end_element)
        else:
            raise Exception('Expected claim text')
            
    def claim(self):
        if self.match(TokenType.DELIMITER_START_CLAIM):
            delimiter_start_claim = self.previous()
            claim_contents = []
            # while not self.match(TokenType.DELIMITER_END_CLAIM):
            #     claim_contents.append(self.claim_content())
            # delimiter_end_claim = self.previous()
            # return Claim(delimiter_start_claim=delimiter_start_claim, claim_content=claim_contents, delimiter_end_claim=delimiter_end_claim)
            while not self.check(TokenType.DELIMITER_START_CLAIM) and not self.is_at_end():
                claim_contents.append(self.claim_content())
            return Claim(delimiter_start_claim=delimiter_start_claim, claim_content=claim_contents)
        else:
            raise Exception('Expected claim start delimiter')
    
    def claims(self):
        claims = []
        while not self.is_at_end():
            # There can be whitespace and text between claims. So we need to chew it up
            # before parsing the next claim.
            while self.match(TokenType.WHITESPACE, TokenType.TEXT):
                continue
            if not self.is_at_end():
                claim = self.claim()
                claims.append(claim)
        return Claims(claims=claims)

    def parse(self):
        return self.claims()

def serialize_claim(claim):
    serialized = ''
    serialized += claim.delimiter_start_claim.lexeme
    for claim_content in claim.claim_content:
        if isinstance(claim_content, ClaimText):
            serialized += claim_content.text.lexeme
        elif isinstance(claim_content, ClaimWhitespace):
            serialized += claim_content.whitespace.lexeme
        elif isinstance(claim_content, ClaimDependency):
            serialized += claim_content.dependency.lexeme
        elif isinstance(claim_content, ClaimDelimiterEndPreamble):
            serialized += claim_content.delimiter_end_preamble.lexeme
        elif isinstance(claim_content, ClaimDelimiterEndElement):
            serialized += claim_content.delimiter_end_element.lexeme
    # serialized += claim.delimiter_end_claim.lexeme
    return serialized

def serialize_claim_elements(claim):
    serialized_claim_elements = []
    # Iterate through claim content, incrementally constructing a claim element. Once a delimiter end preamble or delimiter end element is encountered, add the claim element to the list of claim elements and start a new claim element.
    claim_element = claim.delimiter_start_claim.lexeme
    for claim_content in claim.claim_content:
        if isinstance(claim_content, ClaimText):
            claim_element += claim_content.text.lexeme
        elif isinstance(claim_content, ClaimWhitespace):
            claim_element += claim_content.whitespace.lexeme
        elif isinstance(claim_content, ClaimDependency):
            claim_element += claim_content.dependency.lexeme
        elif isinstance(claim_content, ClaimDelimiterEndPreamble):
            claim_element += claim_content.delimiter_end_preamble.lexeme
            serialized_claim_elements.append(claim_element)
            claim_element = ''
        elif isinstance(claim_content, ClaimDelimiterEndElement):
            claim_element += claim_content.delimiter_end_element.lexeme
            serialized_claim_elements.append(claim_element)
            claim_element = ''
    # Add the last claim element
    # claim_element += claim.delimiter_end_claim.lexeme
    serialized_claim_elements.append(claim_element)
    # Strip whitespace from claim elements
    serialized_claim_elements = [claim_element.strip() for claim_element in serialized_claim_elements]
    return serialized_claim_elements

@dataclass
class TextLine:
    page_number: int
    x0: float
    y0: float
    x1: float
    y1: float
    text: str

@dataclass
class TextLines:
    column_0: list[TextLine]
    column_1: list[TextLine]
    noncolumnar: list[TextLine]


class PDFPageExtremaXStartAndEndAggregator(PDFPageAggregator):
    def __init__(self, rsrcmgr, pageno=1, laparams=None, bottom_margin=50):
        PDFPageAggregator.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)
        """
        Find the median of the 10 highest values for max and the median of the 10 lowest values for min.
        """
        self.lttextline_bbox_min_x0_by_page = {}
        self.lttextline_bbox_max_x1_by_page = {}
        self.bottom_margin = bottom_margin
        self.page_number = 0

    def receive_layout(self, ltpage):        
        def render(item, page_number):
            if isinstance(item, LTPage) or isinstance(item, LTTextBox):
                for child in item:
                    render(child, page_number)
            elif isinstance(item, LTTextLine):
                if item.bbox[1] <= self.bottom_margin:
                    return
                if page_number not in self.lttextline_bbox_min_x0_by_page:
                    self.lttextline_bbox_min_x0_by_page[page_number] = [item.bbox[0]]
                    self.lttextline_bbox_max_x1_by_page[page_number] = [item.bbox[2]]
                else:
                    self.lttextline_bbox_min_x0_by_page[page_number].append(item.bbox[0])
                    self.lttextline_bbox_max_x1_by_page[page_number].append(item.bbox[2])
                    
                for child in item:
                    render(child, page_number)
            return
        render(ltpage, self.page_number)
        # Reduce to median of 10 highest values for max and median of 10 lowest values for min
        if self.page_number in self.lttextline_bbox_min_x0_by_page:
            # If there were no LTTextLine on the page, then we don't have any min or max values to take the median of.
            self.lttextline_bbox_max_x1_by_page[self.page_number] = sorted(self.lttextline_bbox_max_x1_by_page[self.page_number])[-10:]
            self.lttextline_bbox_min_x0_by_page[self.page_number] = sorted(self.lttextline_bbox_min_x0_by_page[self.page_number])[:10]
            # Now take the midpoint
            self.lttextline_bbox_min_x0_by_page[self.page_number] = self.lttextline_bbox_min_x0_by_page[self.page_number][len(self.lttextline_bbox_min_x0_by_page[self.page_number]) // 2]
            self.lttextline_bbox_max_x1_by_page[self.page_number] = self.lttextline_bbox_max_x1_by_page[self.page_number][len(self.lttextline_bbox_max_x1_by_page[self.page_number]) // 2]
        self.page_number += 1
        self.result = ltpage

class PDFPageDetailedAggregator(PDFPageAggregator):
    def __init__(self, rsrcmgr, pageno=1, laparams=None, check_for_div_by_5_line_no=False, bottom_margin=50, lttextline_bbox_min_x0_by_page=None, lttextline_bbox_max_x1_by_page=None, default_to_page_width=True, pages=None):
        PDFPageAggregator.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)
        self.columns = [[],[]]
        # If parsed document is noncolumnar, then this becomes isomorphic to self.rows and self.columns should be empty.
        self.noncolumnar = []
        self.page_bboxes = []
        self.page_number = 0
        self.check_for_div_by_5_line_no = check_for_div_by_5_line_no
        # In points. Any line that is this many points or less from the bottom of the page is considered to be part of the footer and is ignored.
        self.bottom_margin = bottom_margin
        self.default_to_page_width = default_to_page_width
        self.lttextline_bbox_min_x0_by_page = lttextline_bbox_min_x0_by_page
        self.lttextline_bbox_max_x1_by_page = lttextline_bbox_max_x1_by_page

        self.text_lines = []
        self.non_text_lines = []

        self.pages = pages

    def receive_layout(self, ltpage):        
        def render(item, page_number):
            if isinstance(item, LTPage) or isinstance(item, LTTextBox):
                for child in item:
                    render(child, page_number)
            elif isinstance(item, LTTextLine):
                if item.bbox[1] <= self.bottom_margin:
                    return
                self.text_lines.append(item)
                child_str = ''
                for child in item:
                    if isinstance(child, (LTChar, LTAnno)):
                        child_str += child.get_text()
                child_str = ' '.join(child_str.split()).strip()
                if child_str:
                    row = TextLine(page_number, item.bbox[0], item.bbox[1], item.bbox[2], item.bbox[3], child_str) # bbox == (x1, y1, x2, y2)
                    x_center_of_page = ltpage.width / 2
                    # Check ltpage.width and item.bbox values are off by order of magnitude
                    off_by_order_of_magnitude = False
                    if ltpage.width / item.bbox[2] > 10 or item.bbox[2] / ltpage.width > 10:
                        off_by_order_of_magnitude = True
                    if (not self.default_to_page_width or off_by_order_of_magnitude) and self.lttextline_bbox_min_x0_by_page is not None and self.lttextline_bbox_max_x1_by_page is not None and page_number in self.lttextline_bbox_min_x0_by_page and page_number in self.lttextline_bbox_max_x1_by_page:
                        x_center_of_page = (self.lttextline_bbox_min_x0_by_page[page_number] + self.lttextline_bbox_max_x1_by_page[page_number]) / 2
                    if item.bbox[2] <= x_center_of_page:
                        self.columns[0].append(row)
                    elif item.bbox[0] >= x_center_of_page:
                        self.columns[1].append(row)
                    else:
                        if self.check_for_div_by_5_line_no:
                            # If this line is in the left column and its last one or two characters are digits that form an integer divisible by 5, then we assume it is a line number and not part of the text of the patent. Therefore we shouldn't take into account the added character width of the line number when calculating whether the line is in the left or right column. So we'll find the last character before the line number and substitute its x1 value for the item's x1 value.
                            children = list(item)
                            # check if greater overlap with left column or right column
                            # if children[0].get_text() == '5' and page_number == 6 and children[2].get_text() == '\n':
                            #     import pdb; pdb.set_trace()
                            if item.bbox[2] - x_center_of_page < x_center_of_page - item.bbox[0]:
                                # Greater overlap with left column
                                i = -1
                                while children[i].get_text().isspace():
                                    i -= 1
                                if children[i].get_text().isdigit() and int(children[i].get_text()) % 5 == 0:
                                    i -= 1
                                    if len(children) > -i and children[i].get_text().isdigit():
                                        i -= 1
                                    if len(children) > -i:
                                        # Maybe eat more whitespace
                                        while isinstance(children[i], LTAnno) or children[i].get_text().isspace():
                                            i -= 1
                                    # Maybe this is a weird short text line hanging out in the middle of the page
                                    i = max(i, -len(children))
                                    if children[i].x1 <= x_center_of_page:
                                        self.columns[0].append(row)
                                    else:
                                        self.noncolumnar.append(row)
                                else:
                                    self.noncolumnar.append(row)
                            else:
                                # TODO: fix this to mirror the greater overlap with left column branch
                                # Greater overlap with right column
                                # check if first character in line is digit divisible by 5
                                if children[0].get_text().isdigit() and int(children[0].get_text()) % 5 == 0:
                                    new_x0 = item.bbox[0] + children[0].width
                                    row.text = row.text[1:]
                                    if len(children) > 1 and children[1].get_text().isdigit():
                                        new_x0 += children[1].width
                                        row.text = row.text[1:]
                                    
                                    if new_x0 >= x_center_of_page:
                                        self.columns[1].append(row)
                                    else:
                                        self.noncolumnar.append(row)
                                else:
                                    self.noncolumnar.append(row)
                        else:
                            self.noncolumnar.append(row)
                for child in item:
                    render(child, page_number)
            return

        if self.pages is not None and self.page_number not in self.pages:
            # TODO: doesnt really help much probably because whole file still being loaded and processed before this step.
            self.page_number += 1
            return
        render(ltpage, self.page_number)
        self.page_number += 1
        self.page_bboxes.append(ltpage.bbox)
        # self.rows = sorted(self.rows, key = lambda x: (x.page_number, -x.y0, -x.x0))
        cmp_fn = lambda x: (x.page_number, -x.y0)
        self.columns[0] = sorted(self.columns[0], key=cmp_fn)
        self.columns[1] = sorted(self.columns[1], key=cmp_fn)
        self.noncolumnar = sorted(self.noncolumnar, key=cmp_fn)
        self.result = ltpage

def parse_text_lines_from_pdf_path(path: pathlib.Path | str) -> TextLines:
    with open(path, 'rb') as f:
        return parse_text_lines_from_pdf_file_obj(f)

def parse_text_lines_from_pdf_path_simple(path: pathlib.Path | str, **aggregator_params) -> TextLines:
    with open(path, 'rb') as f:
        return parse_text_lines_from_pdf_file_obj_simple(f, **aggregator_params)

def parse_text_lines_from_pdf_file_obj_simple(f: BinaryIO, **aggregator_params) -> TextLines:
    parser = PDFParser(f)
    doc = PDFDocument(parser)

    rsrcmgr = PDFResourceManager()
    # TODO: with default params, if the line number in the center margin precedes text that is too far away in the x direction, then the line number and the text get parsed as two separate lines. This typically happens when the text is indented for some reason, for example, in the claims section of patent (see Ellis patent)
    laparams = LAParams()

    device = PDFPageDetailedAggregator(rsrcmgr, laparams=laparams, **aggregator_params)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)
        # receive the LTPage object for this page
        device.get_result()

    return TextLines(
        column_0=device.columns[0],
        column_1=device.columns[1],
        noncolumnar=device.noncolumnar,
    )

def parse_text_lines_from_pdf_file_obj(f: BinaryIO) -> TextLines:
    parser = PDFParser(f)
    doc = PDFDocument(parser)

    rsrcmgr = PDFResourceManager()
    # TODO: with default params, if the line number in the center margin precedes text that is too far away in the x direction, then the line number and the text get parsed as two separate lines. This typically happens when the text is indented for some reason, for example, in the claims section of patent (see Ellis patent)
    laparams = LAParams()

    # First find the min x0 and max x0 per page
    device = PDFPageExtremaXStartAndEndAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)
        # receive the LTPage object for this page
        device.get_result()

    # Seek file back to beginning and parse again
    f.seek(0)

    device = PDFPageDetailedAggregator(rsrcmgr, laparams=laparams, check_for_div_by_5_line_no=True, lttextline_bbox_min_x0_by_page=device.lttextline_bbox_min_x0_by_page, lttextline_bbox_max_x1_by_page=device.lttextline_bbox_max_x1_by_page)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)
        # receive the LTPage object for this page
        device.get_result()

    return TextLines(
        column_0=device.columns[0],
        column_1=device.columns[1],
        noncolumnar=device.noncolumnar,
    )

# Succeeded by optional whitespace or zeroes
country_code_pattern = r'(?P<country_code>[A-Z]{2})\s*[O0]*'
optional_year = r'(?P<year>[1-2][0-9]{3})?'
# Negative lookahead to make sure patent number pattern doesnt match year. There should be no digits after the patent number 
patent_number_pattern = r'(?P<patent_number>[0-9]{6,8})(?!\d+)'
# Sometimes B1 can be parsed by pdfminer as Bl
kind_code_pattern = r'(?P<kind_code>[A-C]{1}[\dl]?)?'

patent_number_regex = re.compile(country_code_pattern + optional_year + patent_number_pattern + kind_code_pattern)


def find_beginning_of_specification(column_0: list[PatentTextLine], column_1: list[PatentTextLine]) -> int:
    """
    Returns page number, assumes spec starts at first line of page
    """
    def beg_spec_classification_model(page_text):
        keywords = ['BACKGROUND', 'DESCRIPTION', 'SUMMARY']
        for keyword in keywords:
            if keyword in page_text:
                return True
        return False
    
    # Check column 0 
    for text_line in column_0:
        if beg_spec_classification_model(text_line.text):
            return text_line.page_num
    # Check column 1
    for text_line in column_1:
        if beg_spec_classification_model(text_line.text):
            return text_line.page_num
    return None

BeginningOfClaims = namedtuple('BeginningOfClaims', ['page_index', 'col_index', 'line_index'])
EndOfClaims = namedtuple('EndOfClaims', ['page_index', 'col_index', 'line_index'])

def find_beginning_of_claims(column_0: list[PatentTextLine], column_1: list[PatentTextLine]) -> BeginningOfClaims | None:
    """ 
    Returns page number and line number where claims start
    """
    def beg_claims_classification_model(page_text):
        # TODO: replace this with a more robust model
        key_phrases = ['What is claimed is:', 'We claim:', 'I claim:', 'The invention claimed is:', 'The invention claimed is as follows:', 'The invention claimed is:', 'claim:', 'Claims:', 'is claimed is']
        for key_phrase in key_phrases:
            if key_phrase in page_text:
                return True
        return False
    
    # Check column 0
    for text_line in column_0:
        if beg_claims_classification_model(text_line.text):
            return BeginningOfClaims(page_index=text_line.page_num, col_index=0, line_index=text_line.line_index)
        
    # Check column 1
    for text_line in column_1:
        if beg_claims_classification_model(text_line.text):
            return BeginningOfClaims(page_index=text_line.page_num, col_index=1, line_index=text_line.line_index)
    return None

class EndClaimsClassificationModel:
    def __init__(self):
        self.key_phrases = ['k k k k k', '* * * * *']
        self.key_phrases_built = ['' for _ in self.key_phrases]
        self.key_phrase_beginning_line = [None for _ in self.key_phrases]
        self.key_phrases_len = [len(''.join(key_phrase.split())) for key_phrase in self.key_phrases]
        self.key_phrases_iter = [self.iter_key_phrase(key_phrase) for key_phrase in self.key_phrases]

    def iter_key_phrase(self, key_phrase):
        for char in key_phrase:
            if char.isspace():
                continue
            else:
                yield char

    def classify(self, line: PatentTextLine) -> PatentTextLine | None:
        for key_phrase in self.key_phrases:
            if key_phrase in line.text:
                return line
        # Check if key phrase is split across lines
        for i, key_phrase_iter in enumerate(self.key_phrases_iter):
            char = next(key_phrase_iter, None)
            if char == line.text.strip():
                if not self.key_phrases_built[i]:
                    self.key_phrase_beginning_line[i] = line
                self.key_phrases_built[i] += char
                if self.key_phrases_built[i] == ''.join(self.key_phrases[i].split()):
                    return self.key_phrase_beginning_line[i]
            else:
                self.key_phrases_built[i] = ''
                self.key_phrases_iter[i] = self.iter_key_phrase(self.key_phrases[i])
                self.key_phrase_beginning_line[i] = None
        return None

def serialize_lines_with_pointers(lines: list[PatentTextLine]):
    """
    Serialize column-interleaved text lines and return a mapping of pointers to indices in the serialized string for the original patent text lines
    """
    serialized_lines = ''
    pointers = []
    for line in lines:
        pointers.append(len(serialized_lines))
        serialized_lines += line.text
    return serialized_lines, pointers

# def find_end_of_claims(column_0: list[PatentTextLine], column_1: list[PatentTextLine]) -> EndOfClaims:
#     """ 
#     Returns page number and line number where claims end
#     """
#     end_claims_classification_model = EndClaimsClassificationModel()

#     # Check column 0
#     for text_line in column_0:
#         if text_line.page_num == 16:
#             print(text_line.text)
#         found_line = end_claims_classification_model.classify(text_line)
#         if found_line:
#             return EndOfClaims(page_index=found_line.page_num, col_index=0, line_index=found_line.line_index)
        
#     # Check column 1
#     for text_line in column_1:
#         if text_line.page_num == 16:
#             print(text_line.text)
#         found_line = end_claims_classification_model.classify(text_line)
#         if found_line:
#             return EndOfClaims(page_index=found_line.page_num, col_index=1, line_index=found_line.line_index)
#     return None

def find_end_of_claims(column_0: list[PatentTextLine], column_1: list[PatentTextLine], beginning_of_claims: BeginningOfClaims) -> EndOfClaims | None:
    column_interleaved = interleave_patent_text_lines_columns(column_0, column_1)
    # Extract chunk after beginning of claims
    interleaved_claims_start_line = None
    for i in range(len(column_interleaved)):
        if (column_interleaved[i].page_num == beginning_of_claims.page_index 
        and column_interleaved[i].column_index == beginning_of_claims.col_index and column_interleaved[i].line_index == beginning_of_claims.line_index):
            interleaved_claims_start_line = i
            break

    claim_lines = column_interleaved[interleaved_claims_start_line:]
    serialized_lines, pointers = serialize_lines_with_pointers(claim_lines)

    pointers_index = 0
    for i, char in enumerate(serialized_lines):
        if (
            char == '.' 
            and not re.match(claim_number_regex, serialized_lines[pointers[pointers_index]:i+1])  # This period isn't part of the claim's numbering
            and not re.match(claim_number_regex, serialized_lines[pointers[pointers_index+1]:])  # The nThe system of claim 1 , wherein the user input is a firstext line doesn't have claim numbering
            and all(
                c.isspace() for c in claim_lines[pointers_index].text[i - pointers[pointers_index]+1:]
            )  # Check period is at end of the line (sometimes there are spurious periods mid line. If there's a spurious period at the end of a line, we're out of luck)
        ):
            return EndOfClaims(
                page_index=claim_lines[pointers_index].page_num,
                col_index=claim_lines[pointers_index].column_index,
                line_index=claim_lines[pointers_index].line_index
            )

        if pointers_index < len(pointers) - 1 and i == pointers[pointers_index + 1]:
            pointers_index += 1  

    return None

@dataclass
class PatentTextLines:
    column_0: list[PatentTextLine]
    column_1: list[PatentTextLine]
    noncolumnar: list[PatentTextLine]

class ParsedPatent(pydantic.BaseModel):
    unique_id: PatentUniqueID
    text_lines: PatentTextLines
    beginning_of_specification: int
    # Currently optional to accomodate cases where claims don't have clear prefatory language (see example in tests). Should be made not optional
    beginning_of_claims: Optional[BeginningOfClaims]
    end_of_claims: Optional[EndOfClaims]


is_column_num_pattern = r'^\d{1,4}\s*(?:\n|\\n)?\s*$'
is_column_num_regex = re.compile(is_column_num_pattern)

paragraph_num_pattern = r'\s*\[\s*(?P<paragraph_num>\d{4})\s*\]'
paragraph_num_regex = re.compile(paragraph_num_pattern)

def parse_patent_unique_id_from_text_lines(text_lines: TextLines) -> PatentUniqueID | None:
    column_0 = text_lines.column_0
    column_1 = text_lines.column_1
    noncolumnar = text_lines.noncolumnar

    # Search for unique id in the first page of the patent. Start with column 1, because that's usually where it is
    unique_id = None
    for line in column_1:
        # gd pdfs
        text = re.sub(r'\s+', '', line.text)
        text = text.replace('l', '1')
        match = patent_number_regex.search(text)
        if match:
            patent_number = match.groupdict()['patent_number']
            year = match.groupdict()['year']
            if year:
                patent_number = year + patent_number
            kind_code = match.groupdict()['kind_code']
            if kind_code:
                kind_code = kind_code.replace('l', '1')
            unique_id = PatentUniqueID(
                patent_number=patent_number,
                country_code=match.groupdict()['country_code'],
                kind_code=kind_code
            )
            break

    if not unique_id:
        for line in column_0:
            # gd pdfs
            text = re.sub(r'\s+', '', line.text)
            text = text.replace('l', '1')
            match = patent_number_regex.search(text)
            if match:
                patent_number = match.groupdict()['patent_number']
                year = match.groupdict()['year']
                if year:
                    patent_number = year + patent_number
                kind_code = match.groupdict()['kind_code']
                if kind_code:
                    kind_code = kind_code.replace('l', '1')
                unique_id = PatentUniqueID(
                    patent_number=patent_number,
                    country_code=match.groupdict()['country_code'],
                    kind_code=kind_code
                )
                break
    
    if not unique_id:
        for line in noncolumnar:
            # gd pdfs
            text = re.sub(r'\s+', '', line.text)
            text = text.replace('l', '1')
            match = patent_number_regex.search(text)
            if match:
                patent_number = match.groupdict()['patent_number']
                year = match.groupdict()['year']
                if year:
                    patent_number = year + patent_number
                kind_code = match.groupdict()['kind_code']
                if kind_code:
                    kind_code = kind_code.replace('l', '1')
                unique_id = PatentUniqueID(
                    patent_number=patent_number,
                    country_code=match.groupdict()['country_code'],
                    kind_code=kind_code
                )
                break

    return unique_id

def parse_patent_unique_id_from_pdf_path(path: pathlib.Path | str) -> PatentUniqueID | None:
    text_lines = parse_text_lines_from_pdf_path_simple(path, pages=[0])
    return parse_patent_unique_id_from_text_lines(text_lines)

def parse_patent_unique_id_from_pdf_file_obj(f: BinaryIO) -> PatentUniqueID | None:
    text_lines = parse_text_lines_from_pdf_file_obj_simple(f, pages=[0])
    return parse_patent_unique_id_from_text_lines(text_lines)

def parse_patent_from_text_lines(text_lines: TextLines) -> ParsedPatent:
    """ 
    Assumes all arguments sorted first by page number ascending
    """
    column_0 = text_lines.column_0
    column_1 = text_lines.column_1
    noncolumnar = text_lines.noncolumnar

    column_0_patent_text_lines = []
    column_1_patent_text_lines = []
    noncolumnar_patent_text_lines = []

    def is_column_num(line: TextLine, line_index: int):
        return (
            line_index == 0 and
            is_column_num_regex.match(line.text)
        )

    def get_line_num(line: TextLine, line_index: int) -> int:
        """
        If line contains a line number, returns the line number and trims the line number from the line. Otherwise returns None
        """
        # TODO: unify this with the parsing done by the PDFPageDetailedAggregator
        # TODO: currently misses a lot of line numbers because many line numbers are parsed as their own 1-2 character line. Associating the line number with the appropriate line will have to happen upstream, perhaps by appending the line number to the line closest in alignment on the y axis
        if line_index == 0:
            return None
        if len(line.text) < 3:
            # Currently, columnar lines include random text from figures and tables. These lines will be given line numbers, making this function noisy, but we add this simple check just to make sure this function can run without error. We know lines we care about will be at least 3 characters long.
            return None
        candidate_line_num = 0
        # Line number is at beginning of line
        first_char = line.text[0]
        if first_char.isdigit():
            candidate_line_num = first_char
            second_char = line.text[1]
            if second_char.isdigit():
                if line.text[2] == '.':
                    # This is a probably a claim number
                    return None
                candidate_line_num = candidate_line_num + second_char
            elif second_char == '.':
                # This is a probably a claim number
                return None

            # If candidate line number is a multiple of 5, then it is a line number
            if int(candidate_line_num) % 5 == 0:
                # Strip line text of candidate line num
                # TODO: fix because this erroneously strips claim numbers sometimes
                # line.text = line.text[len(candidate_line_num):]
                return int(candidate_line_num)
            
        # Line number is at end of line
        last_char = line.text.rstrip('\n')[-1]
        if last_char.isdigit():
            candidate_line_num = last_char
            second_to_last_char = line.text.rstrip('\n')[-2]
            if second_to_last_char.isdigit():
                candidate_line_num = second_to_last_char + candidate_line_num
            # If candidate line number is a multiple of 5, then it is a line number
            if int(candidate_line_num) % 5 == 0:
                # Strip line text of candidate line num
                # TODO: fix because this erroneously strips claim numbers sometimes
                # line.text = line.text[:-(len(candidate_line_num))]
                return int(candidate_line_num)
        return None

    def get_paragraph_num(line: TextLine):
        match = paragraph_num_regex.match(line.text)
        if match:
            return int(match.groupdict()['paragraph_num'])
        return None

    # Search for unique id in the first page of the patent. Start with column 1, because that's usually where it is
    unique_id = None
    for line in column_1:
        # gd pdfs
        text = re.sub(r'\s+', '', line.text)
        text = text.replace('l', '1')
        match = patent_number_regex.search(text)
        if match:
            patent_number = match.groupdict()['patent_number']
            year = match.groupdict()['year']
            if year:
                patent_number = year + patent_number
            kind_code = match.groupdict()['kind_code']
            if kind_code:
                kind_code = kind_code.replace('l', '1')
            unique_id = PatentUniqueID(
                patent_number=patent_number,
                country_code=match.groupdict()['country_code'],
                kind_code=kind_code
            )
            break

    if not unique_id:
        for line in column_0:
            # gd pdfs
            text = re.sub(r'\s+', '', line.text)
            text = text.replace('l', '1')
            match = patent_number_regex.search(text)
            if match:
                patent_number = match.groupdict()['patent_number']
                year = match.groupdict()['year']
                if year:
                    patent_number = year + patent_number
                kind_code = match.groupdict()['kind_code']
                if kind_code:
                    kind_code = kind_code.replace('l', '1')
                unique_id = PatentUniqueID(
                    patent_number=patent_number,
                    country_code=match.groupdict()['country_code'],
                    kind_code=kind_code
                )
                break
    
    if not unique_id:
        for line in noncolumnar:
            # gd pdfs
            text = re.sub(r'\s+', '', line.text)
            text = text.replace('l', '1')
            match = patent_number_regex.search(text)
            if match:
                patent_number = match.groupdict()['patent_number']
                year = match.groupdict()['year']
                if year:
                    patent_number = year + patent_number
                kind_code = match.groupdict()['kind_code']
                if kind_code:
                    kind_code = kind_code.replace('l', '1')
                unique_id = PatentUniqueID(
                    patent_number=patent_number,
                    country_code=match.groupdict()['country_code'],
                    kind_code=kind_code
                )
                break

    line_index = 0
    current_page_num = 0
    column_num = None
    paragraph_num = None
    for line in column_0:
        page_num = line.page_number
        if page_num != current_page_num:
            line_index = 0
            current_page_num = page_num
        if is_column_num(line, line_index):
            column_num = int(line.text.rstrip('\n'))
            if column_num % 2 == 0:
                logger.error(
                    f'Column number {column_num} unexpectedly even. Patent: {unique_id} -- Line: {line}'
                )
                column_num = None
            
            # NOTE: don't include column number lines in the parsed text
            continue

        if line.text.strip().isdigit() and int(line.text.strip()) % 5 == 0:
            # TODO: for now we just throw away standalone line numbers. See comment in get_line_num
            continue

        # TODO: currently only adds line number to line that has the numbering. Should add line number to each line based on the line's offset from the last line with an explicit numbering
        line_num = get_line_num(line, line_index)
        new_paragraph_num = get_paragraph_num(line)
        if new_paragraph_num is not None:
            paragraph_num = new_paragraph_num
        column_0_patent_text_lines.append(
            PatentTextLine(
                page_num=line.page_number, 
                text=line.text, 
                line_index=line_index, 
                column_index=0,
                column_num=column_num,
                line_num=line_num,
                paragraph_num=paragraph_num
            )
        )

        line_index += 1

    line_index = 0
    current_page_num = 0
    column_num = None
    paragraph_num = None
    for line in column_1:
        page_num = line.page_number
        if page_num != current_page_num:
            line_index = 0
            current_page_num = page_num
        if is_column_num(line, line_index):
            column_num = int(line.text.rstrip('\n'))
            if column_num % 2 == 1:
                logger.error(
                    f'Column number {column_num} unexpectedly odd. Patent: {unique_id} -- Line: {line}'
                )
                column_num = None
            
            # NOTE: don't include column number lines in the parsed text
            continue

        if line.text.strip().isdigit() and int(line.text.strip()) % 5 == 0:
            # TODO: for now we just throw away standalone line numbers. See comment in get_line_num
            continue

        line_num = get_line_num(line, line_index)
        paragraph_num = get_paragraph_num(line)
        if new_paragraph_num is not None:
            paragraph_num = new_paragraph_num
        column_1_patent_text_lines.append(
            PatentTextLine(
                page_num=line.page_number, 
                text=line.text, 
                line_index=line_index, 
                column_index=1,
                column_num=column_num,
                line_num=line_num,
                paragraph_num=paragraph_num
            )
        )

        line_index += 1

    line_index = 0
    current_page_num = 0
    for line in noncolumnar:
        page_num = line.page_number
        if page_num != current_page_num:
            line_index = 0
            current_page_num = page_num
        noncolumnar_patent_text_lines.append(
            PatentTextLine(
                page_num=line.page_number, 
                text=line.text, 
                line_index=line_index, 
                column_index=None,
                column_num=None,
                line_num=None,
                paragraph_num=None
            )
        )

        line_index += 1
    
    beginning_of_claims = find_beginning_of_claims(column_0_patent_text_lines, column_1_patent_text_lines)
    end_of_claims = find_end_of_claims(column_0_patent_text_lines, column_1_patent_text_lines, beginning_of_claims)

    return ParsedPatent(
        unique_id=unique_id,
        text_lines=PatentTextLines(
            column_0=column_0_patent_text_lines,
            column_1=column_1_patent_text_lines,
            noncolumnar=noncolumnar_patent_text_lines,
        ),
        beginning_of_specification=find_beginning_of_specification(column_0_patent_text_lines, column_1_patent_text_lines),
        beginning_of_claims=beginning_of_claims,
        end_of_claims=end_of_claims
    )

def parse_patent_from_pdf_path(path: pathlib.Path | str) -> ParsedPatent:
    text_lines = parse_text_lines_from_pdf_path(path)
    return parse_patent_from_text_lines(text_lines)

def parse_patent_from_pdf_file_obj(f: BinaryIO) -> ParsedPatent | None:
    text_lines = parse_text_lines_from_pdf_file_obj(f)
    return parse_patent_from_text_lines(text_lines)

def parse_google_patent_from_pdf_path(path: pathlib.Path | str) -> GoogleParsedPatent:
    unique_id = parse_patent_unique_id_from_pdf_path(path)
    if unique_id is None:
        raise ParseError(f'Could not parse unique id from patent')

    return parse_google_patent(unique_id)

def parse_google_patent_from_pdf_file_obj(f: BinaryIO) -> GoogleParsedPatent:
    unique_id = parse_patent_unique_id_from_pdf_file_obj(f)
    if unique_id is None:
        raise ParseError(f'Could not parse unique id from patent')

    return parse_google_patent(unique_id)
    

def parse_google_patent_from_unique_id(unique_id: str) -> GoogleParsedPatent:
    unique_id = unique_id.replace('-', '')
    match = patent_number_regex.search(unique_id)
    parsed_unique_id = None
    if match:
        patent_number = match.groupdict()['patent_number']
        year = match.groupdict()['year']
        if year:
            patent_number = year + patent_number
        kind_code = match.groupdict()['kind_code']
        parsed_unique_id = PatentUniqueID(
            patent_number=patent_number,
            country_code=match.groupdict()['country_code'],
            kind_code=kind_code
        )
    else:
        raise ParseError(f'Could not parse unique id {unique_id}')
    
    google_patent = parse_google_patent(parsed_unique_id)

    return google_patent

def interleave_patent_text_lines_columns(column_0: list[PatentTextLine], column_1: list[PatentTextLine]) -> list[PatentTextLine]:
    """
    Assumes column_0 and column_1 are sorted by page number, then by line index
    """
    interleaved = []
    i = 0
    j = 0
    while i < len(column_0) and j < len(column_1):
        if column_0[i].page_num <= column_1[j].page_num:
            interleaved.append(column_0[i])
            i += 1
        else:
            interleaved.append(column_1[j])
            j += 1
    return interleaved

def group_parsed_patent_by_page(parsed_patent: ParsedPatent) -> dict[int, PatentTextLines]:
    pages_to_patent_text_lines = {}
    for text_line in parsed_patent.text_lines.column_0:
        if text_line.page_num not in pages_to_patent_text_lines:
            pages_to_patent_text_lines[text_line.page_num] = PatentTextLines(
                column_0=[],
                column_1=[],
                noncolumnar=[]
            )
        pages_to_patent_text_lines[text_line.page_num].column_0.append(text_line)

    for text_line in parsed_patent.text_lines.column_1:
        if text_line.page_num not in pages_to_patent_text_lines:
            pages_to_patent_text_lines[text_line.page_num] = PatentTextLines(
                column_0=[],
                column_1=[],
                noncolumnar=[]
            )
        pages_to_patent_text_lines[text_line.page_num].column_1.append(text_line)

    for text_line in parsed_patent.text_lines.noncolumnar:
        if text_line.page_num not in pages_to_patent_text_lines:
            pages_to_patent_text_lines[text_line.page_num] = PatentTextLines(
                column_0=[],
                column_1=[],
                noncolumnar=[]
            )
        pages_to_patent_text_lines[text_line.page_num].noncolumnar.append(text_line)

    return pages_to_patent_text_lines

@dataclass
class PatentWord:
    text:str
    line: PatentTextLine

def flatten_parsed_patent_to_words(parsed_patent: ParsedPatent) -> list[PatentWord]:
    """
    Returns a list of words from the columnar lines of the patent, ordered by page then by column then by line index.
    """
    lines_by_page = group_parsed_patent_by_page(parsed_patent)
    words: list[PatentWord] = []
    for _, lines in lines_by_page.items():
        for line in lines.column_0:
            words.extend(
                PatentWord(
                    text=word,
                    line=line,
                )
                for word in line.text.split()
            )
        for line in lines.column_1:
            words.extend(
                PatentWord(
                    text=word,
                    line=line,
                )
                for word in line.text.split()
            )
    return words

def serialize_claims_from_parsed_patent(parsed_patent: ParsedPatent) -> list[str]:
    """
    Extract text from beginning of claims to end of claims.
    """
    by_page = group_parsed_patent_by_page(parsed_patent)
    serialized_claims = []
    claim_beg_page = parsed_patent.beginning_of_claims.page_index
    claim_beg_col = parsed_patent.beginning_of_claims.col_index
    # Add one because we don't want to include the prefatory text
    claim_beg_line = parsed_patent.beginning_of_claims.line_index + 1
    claim_end_page = parsed_patent.end_of_claims.page_index
    claim_end_col = parsed_patent.end_of_claims.col_index
    claim_end_line = parsed_patent.end_of_claims.line_index

    # Get text from beginning to end
    if claim_beg_page == claim_end_page:
        page = by_page[claim_beg_page]
        # Get text from beginning of claims to end of claims
        if claim_beg_col == 0 and claim_end_col == 0:
            # Get text from beginning in column 0 to end in column 0
            for text_line in page.column_0[claim_beg_line:claim_end_line]:
                serialized_claims.append(text_line.text)
        elif claim_beg_col == 0:
            # Get text from beginning in column 0 to end in column 1
            for text_line in page.column_0[claim_beg_line:]:
                serialized_claims.append(text_line.text)
            for text_line in page.column_1[:claim_end_line]:
                serialized_claims.append(text_line.text)
        else:
            # Get text from beginning in column 1 to end in column 1
            for text_line in page.column_1[claim_beg_line:claim_end_line]:
                serialized_claims.append(text_line.text)
    else:
        for page_num in range(claim_beg_page, claim_end_page + 1):
            page = by_page[page_num]
            if page_num == claim_beg_page:
                # Get text from beginning of claims to end of page
                if claim_beg_col == 0:
                    # Get text from beginning of claims to end of column 0
                    for text_line in page.column_0[claim_beg_line:]:
                        serialized_claims.append(text_line.text)
                    for text_line in page.column_1:
                        serialized_claims.append(text_line.text)
                else:
                    # Get text from beginning of claims to end of column 1
                    for text_line in page.column_1[claim_beg_line:]:
                        serialized_claims.append(text_line.text)
            elif page_num == claim_end_page:
                # Get text from beginning of page to end of claims
                if claim_end_col == 0:
                    # Get text from beginning of column 0 to end of claims
                    for text_line in page.column_0[:claim_end_line]:
                        serialized_claims.append(text_line.text)
                else:
                    # Get text from beginning of column 1 to end of claims
                    for text_line in page.column_0:
                        serialized_claims.append(text_line.text)
                    for text_line in page.column_1[:claim_end_line]:
                        serialized_claims.append(text_line.text)
            else:
                # Get text from beginning of page to end of page
                for text_line in page.column_0:
                    serialized_claims.append(text_line.text)
                for text_line in page.column_1:
                    serialized_claims.append(text_line.text)

    return serialized_claims

def serialize_specification_from_parsed_patent(parsed_patent: ParsedPatent) -> list[str]:
    """
    Extract the specifiction from the parsed patent. We assume the specification ends at the beginning of the claims. We assume the specification starts at the beginning of the first page of the specification. We assume the specification starts at the beginning of the first column of the first page of the specification.
    """
    by_page = group_parsed_patent_by_page(parsed_patent)
    serialized_spec = []
    beg_spec_page = parsed_patent.beginning_of_specification
    beg_spec_line = 0
    claim_beg_page = parsed_patent.beginning_of_claims.page_index
    claim_beg_col = parsed_patent.beginning_of_claims.col_index
    claim_beg_line = parsed_patent.beginning_of_claims.line_index
    # We'll allow claim_beg_page to be None if the claims are not found. In this case, we'll just serialize the entire specification, including the claims.
    if claim_beg_page is None:
        claim_beg_page = len(by_page) - 1

    # Get text from beginning to end
    for page_num in range(beg_spec_page, claim_beg_page + 1):
        page = by_page[page_num]
        if page_num == beg_spec_page:
            # Get text from beginning of specification to end of page. We assume spec begins at the beginning of col 0 of the first page of the spec.
            for text_line in page.column_0[beg_spec_line:]:
                serialized_spec.append(text_line.text)
            for text_line in page.column_1:
                serialized_spec.append(text_line.text)
        elif page_num == claim_beg_page:
            # Get text from beginning of page to beginning of claims
            if claim_beg_col == 0:
                # Get text from beginning of column 0 to beginning of claims
                for text_line in page.column_0[:claim_beg_line]:
                    serialized_spec.append(text_line.text)
            else:
                # Get text from beginning of column 1 to beginning of claims
                for text_line in page.column_0:
                    serialized_spec.append(text_line.text)
                for text_line in page.column_1[:claim_beg_line]:
                    serialized_spec.append(text_line.text)
        else:
            # Get text from beginning of page to end of page
            for text_line in page.column_0:
                serialized_spec.append(text_line.text)
            for text_line in page.column_1:
                serialized_spec.append(text_line.text)

    return serialized_spec

def parse_claims_from_parsed_patent(parsed_patent: ParsedPatent) -> Claims:
    serialized_claims = serialize_claims_from_parsed_patent(parsed_patent)
    claim_text = ''.join(serialized_claims)
    tokens = lex_claims(claim_text)
    parser = ClaimsParser(tokens)
    return parser.parse()


def chunk_spec_from_parsed_patent(parsed_patent, chunk_word_count=250):
    """
    Splits on a period that occurs anywhere within the text line rather than just at the end, leading to more accurate word count chunks.
    """
    by_page = group_parsed_patent_by_page(parsed_patent)
    chunks = []
    beg_spec_page = parsed_patent.beginning_of_specification
    beg_spec_line = 0
    claim_beg_page = parsed_patent.beginning_of_claims.page_index
    claim_beg_col = parsed_patent.beginning_of_claims.col_index
    claim_beg_line = parsed_patent.beginning_of_claims.line_index
    # We'll allow claim_beg_page to be None if the claims are not found. In this case, we'll just serialize the entire specification, including the claims.
    if claim_beg_page is None:
        claim_beg_page = len(by_page) - 1

    def count_words_in_chunk(chunk):
        return sum([len(text_line.text.split()) for text_line in chunk])

    chunk = []
    # Get text from beginning to end
    for page_num in range(beg_spec_page, claim_beg_page + 1):
        page = by_page[page_num]
        if page_num == beg_spec_page:
            # Get text from beginning of specification to end of page. We assume spec begins at the beginning of col 0 of the first page of the spec.
            for text_line in page.column_0[beg_spec_line:]:
                if '.' in text_line.text:
                    # split on period into two text lines
                    split_text = text_line.text.split('.')
                    # copy text line and replace text with first half of split
                    text_line_before_period = copy.copy(text_line)
                    text_line_before_period.text = split_text[0] + '.'
                    text_line_after_period = copy.copy(text_line)
                    text_line_after_period.text = split_text[1].lstrip()

                    if count_words_in_chunk(chunk) + len(text_line.text.split()) >= chunk_word_count:
                        chunk.append(text_line_before_period)
                        chunks.append(chunk)
                        chunk = []
                        if text_line_after_period.text:
                            chunk.append(text_line_after_period)
                else:
                    chunk.append(text_line)
            for text_line in page.column_1:
                if '.' in text_line.text:
                    # split on period into two text lines
                    split_text = text_line.text.split('.')
                    # copy text line and replace text with first half of split
                    text_line_before_period = copy.copy(text_line)
                    text_line_before_period.text = split_text[0] + '.'
                    text_line_after_period = copy.copy(text_line)
                    text_line_after_period.text = split_text[1].lstrip()

                    if count_words_in_chunk(chunk) + len(text_line.text.split()) >= chunk_word_count:
                        chunk.append(text_line_before_period)
                        chunks.append(chunk)
                        chunk = []
                        if text_line_after_period.text:
                            chunk.append(text_line_after_period)
                else:
                    chunk.append(text_line)
        elif page_num == claim_beg_page:
            # Get text from beginning of page to beginning of claims
            if claim_beg_col == 0:
                # Get text from beginning of column 0 to beginning of claims
                for text_line in page.column_0[:claim_beg_line]:
                    if '.' in text_line.text:
                        # split on period into two text lines
                        split_text = text_line.text.split('.')
                        # copy text line and replace text with first half of split
                        text_line_before_period = copy.copy(text_line)
                        text_line_before_period.text = split_text[0] + '.'
                        text_line_after_period = copy.copy(text_line)
                        text_line_after_period.text = split_text[1].lstrip()

                        if count_words_in_chunk(chunk) + len(text_line.text.split()) >= chunk_word_count:
                            chunk.append(text_line_before_period)
                            chunks.append(chunk)
                            chunk = []
                            if text_line_after_period.text:
                                chunk.append(text_line_after_period)
                    else:
                        chunk.append(text_line)
            else:
                # Get text from beginning of column 1 to beginning of claims
                for text_line in page.column_0:
                    if '.' in text_line.text:
                        # split on period into two text lines
                        split_text = text_line.text.split('.')
                        # copy text line and replace text with first half of split
                        text_line_before_period = copy.copy(text_line)
                        text_line_before_period.text = split_text[0] + '.'
                        text_line_after_period = copy.copy(text_line)
                        text_line_after_period.text = split_text[1].lstrip()

                        if count_words_in_chunk(chunk) + len(text_line.text.split()) >= chunk_word_count:
                            chunk.append(text_line_before_period)
                            chunks.append(chunk)
                            chunk = []
                            if text_line_after_period.text:
                                chunk.append(text_line_after_period)
                    else:
                        chunk.append(text_line)
                for text_line in page.column_1[:claim_beg_line]:
                    if '.' in text_line.text:
                        # split on period into two text lines
                        split_text = text_line.text.split('.')
                        # copy text line and replace text with first half of split
                        text_line_before_period = copy.copy(text_line)
                        text_line_before_period.text = split_text[0] + '.'
                        text_line_after_period = copy.copy(text_line)
                        text_line_after_period.text = split_text[1].lstrip()

                        if count_words_in_chunk(chunk) + len(text_line.text.split()) >= chunk_word_count:
                            chunk.append(text_line_before_period)
                            chunks.append(chunk)
                            chunk = []
                            if text_line_after_period.text:
                                chunk.append(text_line_after_period)
                    else:
                        chunk.append(text_line)
        else:
            # Get text from beginning of page to end of page
            for text_line in page.column_0:
                if '.' in text_line.text:
                    # split on period into two text lines
                    split_text = text_line.text.split('.')
                    # copy text line and replace text with first half of split
                    text_line_before_period = copy.copy(text_line)
                    text_line_before_period.text = split_text[0] + '.'
                    text_line_after_period = copy.copy(text_line)
                    text_line_after_period.text = split_text[1].lstrip()

                    if count_words_in_chunk(chunk) + len(text_line.text.split()) >= chunk_word_count:
                        chunk.append(text_line_before_period)
                        chunks.append(chunk)
                        chunk = []
                        if text_line_after_period.text:
                            chunk.append(text_line_after_period)
                else:
                    chunk.append(text_line)
            for text_line in page.column_1:
                if '.' in text_line.text:
                    # split on period into two text lines
                    split_text = text_line.text.split('.')
                    # copy text line and replace text with first half of split
                    text_line_before_period = copy.copy(text_line)
                    text_line_before_period.text = split_text[0] + '.'
                    text_line_after_period = copy.copy(text_line)
                    text_line_after_period.text = split_text[1].lstrip()

                    if count_words_in_chunk(chunk) + len(text_line.text.split()) >= chunk_word_count:
                        chunk.append(text_line_before_period)
                        chunks.append(chunk)
                        chunk = []
                        if text_line_after_period.text:
                            chunk.append(text_line_after_period)
                else:
                    chunk.append(text_line)

    return chunks

def serialize_chunk(chunk):
    return ''.join([text_line.text for text_line in chunk])