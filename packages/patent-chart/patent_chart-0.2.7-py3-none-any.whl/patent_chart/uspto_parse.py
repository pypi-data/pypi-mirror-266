import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

from .parser import PatentUniqueID
from . import search_index

MAX_SEQ_LENGTH = 8191
MAX_BATCH_SIZE=2048

oai = OpenAI()


def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def extract_patent_unique_id(xml: ET.Element) -> PatentUniqueID | None:
    """
    Extract unique id given patent xml root
    """
    doc_id = xml.find('.//us-bibliographic-data-grant/publication-reference/document-id')
    if doc_id is None:
        return None
    try:
        country_code = doc_id.find('.//country').text
        patent_number = doc_id.find('.//doc-number').text
    except AttributeError:
        return None
    # For some reason some patent numbers have leading zeros
    patent_number = patent_number.lstrip('0')
    kind_code = doc_id.find('.//kind')
    if kind_code is not None:
        kind_code = kind_code.text
    return PatentUniqueID(patent_number=patent_number, country_code=country_code, kind_code=kind_code)


def extract_application_filing_date(xml: ET.Element) -> str:
    """
    Extract application filing date given patent xml root
    """
    app_filing_date = xml.find('.//us-bibliographic-data-grant/application-reference/document-id/date')
    return f'{app_filing_date.text[:4]}-{app_filing_date.text[4:6]}-{app_filing_date.text[6:]}'


def extract_priority_date(xml: ET.Element) -> str | None:
    """
    Extract priority date given patent xml root returns in YYYY-MM-DD
    """
    priority_claim = xml.find(".//priority-claim[@sequence='01']")
    
    if priority_claim is not None:
        date_element = priority_claim.find("date")
        if date_element is not None:
            return f'{date_element.text[:4]}-{date_element.text[4:6]}-{date_element.text[6:]}'
    
    provisional_application = xml.find(".//us-provisional-application")
    if provisional_application is not None:
        date_element = provisional_application.find(".//date")
        if date_element is not None:
            return f'{date_element.text[:4]}-{date_element.text[4:6]}-{date_element.text[6:]}'
    
    us_related_docs = xml.find(".//us-related-documents")
    if us_related_docs is not None:
        parent_date = us_related_docs.find(".//continuation/relation/parent-doc/document-id/date")
        if parent_date is not None:
            return f'{parent_date.text[:4]}-{parent_date.text[4:6]}-{parent_date.text[6:]}'
        
    return None


def extract_title(xml):
    title = xml.find('.//invention-title')
    if title is None:
        return ''
    return title.text


def extract_claims(xml: ET.Element):
    claims = xml.find('.//claims')
    return claims


def extract_written_description(xml: ET.Element):
    description = xml.find('.//description')
    return description


def extract_written_description_text(description: ET.Element) -> str:
    text = ''
    for elem in description:
        if elem.tag not in ['p', 'heading']:
            elem_text = '\n'.join([extract_text_recursive(child) for child in elem])
        else:
            elem_text = extract_text_recursive(elem)
        text += elem_text + '\n'
        if elem.tag == 'p':
            text += '\n'
    return text


def extract_text_recursive(element: ET.Element):
    text = ''
    if element.text:
        text += element.text
    for child in element:
        text += extract_text_recursive(child)
    if element.tail:
        text += element.tail
    return text


def chunk_claims(claims: ET.Element) -> list[str]:
    claims_texts = []

    for claim in claims:
        text = extract_text_recursive(claim).strip()
        claims_texts.append(text[:MAX_SEQ_LENGTH])  # HACK: for now, just truncating

    return claims_texts


def chunk_written_description(description: ET.Element, chunk_size_words=512, chunk_overlap_words=128) -> list[str]:
    text = ''
    for elem in description:
        if elem.tag not in ['p', 'heading']:
            elem_text = ' '.join([extract_text_recursive(child) for child in elem])
        else:
            elem_text = extract_text_recursive(elem)
        text += elem_text
        if elem.tag == 'p':
            text += '\n'

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name='gpt-4',
        chunk_size=chunk_size_words,
        chunk_overlap=chunk_overlap_words,
    )

    chunks = text_splitter.split_text(text)
    return chunks


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


def should_drop(patent_unique_id: PatentUniqueID) -> bool:
    """
    Determine if the xml should be dropped
    """
    if patent_unique_id and patent_unique_id.kind_code not in ['B1', 'B2', 'A1', 'A2', 'A9']:
        return True
    return False