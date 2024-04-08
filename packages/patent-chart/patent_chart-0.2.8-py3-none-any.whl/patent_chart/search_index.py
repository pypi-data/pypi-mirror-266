import typing

from elasticsearch import Elasticsearch

from . import settings
from . import parser

client = Elasticsearch(settings.ELASTIC_HOST)

XML_USPTO_POST_2001 = 'xml_uspto_post_2001'


class IndexedPatent(parser.GoogleParsedPatent):
    summary: typing.Optional[str] = None
    short_summary: typing.Optional[str] = None
    topics: typing.Optional[typing.List[str]] = None
    text: typing.Optional[str] = None
    text_format: typing.Optional[str] = None


claim_embedding_scheme = {
    "properties": {
        "patent_doc_id": {
            "type": "keyword"
        },
        "claim_id": {
            "type": "keyword"
        },
        "embedding": {
            "type": "dense_vector",
            "dims": 1024
        },
        'filing_date': {
            'type': 'date'
        },
        'priority_date': {
            'type': 'date'
        }
    }
}


specification_embedding_scheme = {
    "properties": {
        "patent_doc_id": {
            "type": "keyword"
        },
        "paragraph_id": {
            "type": "keyword"
        },
        "embedding": {
            "type": "dense_vector",
            "dims": 1024
        },
        'filing_date': {
            'type': 'date'
        },
        'priority_date': {
            'type': 'date'
        }
    }
}


patent_scheme = {
    "properties": {
        "unique_id": {
            "properties": {
                "patent_number": {
                    "type": "keyword"
                },
                "country_code": {
                    "type": "keyword"
                },
                "kind_code": {
                    "type": "keyword"
                },
            }
        },
        "claims": {
            "type": "text"
        },
        'claims_format': {
            'properties': {
                'data_format': {
                    'type': 'keyword'
                },
                'tree_structure': {
                    'type': 'keyword'
                }
            }
        },
        'specification': {
            "type": "text"
        },
        'specification_format': {
            'properties': {
                'data_format': {
                    'type': 'keyword'
                },
                'tree_structure': {
                    'type': 'keyword'
                }
            }
        },
        'title': {
            'type': 'text'
        },
        'summary': {
            'type': 'text'
        },
        'summary_model_version': {
            'type': 'keyword'
        },
        'short_summary': {
            'type': 'text'
        },
        'short_summary_model_version': {
            'type': 'keyword'
        },
        'topics': {
            'type': 'keyword'
        },
        'topics_model_version': {
            'type': 'keyword'
        },
        'text': {
            'type': 'text'
        },
        'text_format': {
            'type': 'keyword'
        },
        'filing_date': {
            'type': 'date'
        },
        'priority_date': {
            'type': 'date'
        }
    }
}


def create_specification_embedding_index():
    try:
        client.indices.create(index='patents_specification_embedding')
    except Exception as e:
        pass
    client.indices.put_mapping(index='patents_specification_embedding', body=specification_embedding_scheme)


def create_claim_embedding_index():
    try:
        client.indices.create(index='patents_claim_embedding')
    except Exception as e:
        pass
    client.indices.put_mapping(index='patents_claim_embedding', body=claim_embedding_scheme)


def create_patents_index():
    try:
        client.indices.create(index='patents')
    except Exception as e:
        pass
    client.indices.put_mapping(index='patents', body=patent_scheme)


def index_patent(unique_id, text, title, text_format=None, filing_date=None, priority_date=None):
    body = {
        "unique_id": {
            "patent_number": unique_id.patent_number,
            "kind_code": unique_id.kind_code,
            "country_code": unique_id.country_code
        },
        "text": text,
        "title": title
    }

    if text_format:
        body['text_format'] = text_format
    else:
        body['text_format'] = XML_USPTO_POST_2001

    if filing_date:
        body['filing_date'] = filing_date

    if priority_date:
        body['priority_date'] = priority_date
        
    client.index(index='patents', id=str(unique_id), body=body)
    return str(unique_id)


def index_claim_embedding(patent_doc_id, embedding, claim_id=None):
    body = {
        "patent_doc_id": patent_doc_id,
        "embedding": embedding
    }
    if claim_id:
        body['claim_id'] = claim_id

    client.index(index='patents_claim_embedding', body=body)


def index_specification_embedding(patent_doc_id, embedding, paragraph_id=None):
    body = {
        "patent_doc_id": patent_doc_id,
        "embedding": embedding
    }
    if paragraph_id:
        body['paragraph_id'] = paragraph_id
    client.index(index='patents_specification_embedding', body=body)


def get_patent_summary(patent: parser.GoogleParsedPatent) -> str:
    response = client.get(index='patents', id=str(patent.unique_id))
    return response['_source'].get('summary')


def update_patent_by_id(patent: parser.GoogleParsedPatent, **kwargs):
    client.update(index='patents', id=str(patent.unique_id), body={'doc': kwargs})


def patent_exists(patent_unique_id: parser.PatentUniqueID | str) -> bool:
    try:
        client.get(index='patents', id=str(patent_unique_id))
        return True
    except Exception as e:
        return False
    

def get_patent_content_by_id(patent_id: str) -> IndexedPatent | None:
    try:
        response = client.get(index='patents', id=patent_id)
    except Exception as e:
        logger.error('Patent id %s not found in the index', patent_id)
        return None
    return IndexedPatent(**response['_source'])