import datetime
import logging

from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import PineconeException
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_not_exception_message,
    retry_if_not_exception_type
) 

logger = logging.getLogger(__name__) 
pc = Pinecone()

class IndexError(Exception):
    pass

spec_index = pc.Index("patents-spec-embedding")
claims_index = pc.Index("patents-claim-embedding")


def doc_with_prefix_exists(index, prefix):
    try:
        next(index.list(prefix=prefix))
        return True
    except StopIteration:
        return False


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True, retry=retry_if_not_exception_type(IndexError))
def index_spec_embeddings(patent_doc_id:str, filing_date:str, priority_date:str, embeddings:list[list[float]], positions:list[tuple[int]], retry=retry_if_not_exception_type(PineconeException)):
    if filing_date:
        filing_unix_timestamp = datetime.datetime.strptime(filing_date, "%Y-%m-%d").timestamp()
    if priority_date:
        priority_unix_timestamp = datetime.datetime.strptime(priority_date, "%Y-%m-%d").timestamp()

    
    vectors = []
    for i, embedding in enumerate(embeddings):
        metadata = {
            "patent_doc_id": patent_doc_id, 
            "start_pos": positions[i][0], 
            "end_pos": positions[i][1]
        }
        if filing_date:
            metadata["filing_unix_timestamp"] = filing_unix_timestamp
        if priority_date:
            metadata["priority_unix_timestamp"] = priority_unix_timestamp
        
        vectors.append({
            "id": f"{patent_doc_id}-{i}", 
            "values": embedding,
            "metadata": metadata,
        })

    if not vectors:
        raise IndexError("No spec embeddings to index")

    spec_index.upsert(vectors)


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True, retry=retry_if_not_exception_type(IndexError))
def index_claim_embeddings(patent_doc_id:str, filing_date:str, priority_date:str, embeddings:list[list[float]]):
    if filing_date:
        filing_unix_timestamp = datetime.datetime.strptime(filing_date, "%Y-%m-%d").timestamp()
    if priority_date:
        priority_unix_timestamp = datetime.datetime.strptime(priority_date, "%Y-%m-%d").timestamp()

    vectors = []
    for i, embedding in enumerate(embeddings, start=1):
        metadata = {
            "patent_doc_id": patent_doc_id, 
            "claim_id": i
        }
        if filing_date:
            metadata["filing_unix_timestamp"] = filing_unix_timestamp
        if priority_date:
            metadata["priority_unix_timestamp"] = priority_unix_timestamp
        
        vectors.append({
            "id": f"{patent_doc_id}-{i-1}", 
            "values": embedding,
            "metadata": metadata,
        })

    if not vectors:
        raise IndexError("No claim embeddings to index")

    claims_index.upsert(vectors)


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True)
def query_spec_embedding(query: list[float], top_k: int, filter: dict | None = None, **kwargs):
    return spec_index.query(query, top_k=top_k, filter=filter, **kwargs)['matches']


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True)
def get_claim_embeddings_by_patent_doc_id(patent_doc_id:str):
    ids = list(claims_index.list(prefix=patent_doc_id))
    if not ids:
        return []
    ids = ids[0]
    records = claims_index.fetch(ids)
    return records['vectors']


def get_claim_embeddings_values_by_patent_doc_id(patent_doc_id:str):
    values = []
    records = get_claim_embeddings_by_patent_doc_id(patent_doc_id)
    for record in records:
        record_values = records[record]['values']
        values.append(record_values)
    return values


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True)
def get_spec_embeddings_by_patent_doc_id(patent_doc_id:str):
    ids = list(spec_index.list(prefix=patent_doc_id))
    if not ids:
        return []
    ids = ids[0]
    records = spec_index.fetch(ids)
    return records['vectors']


def get_spec_embeddings_values_by_patent_doc_id(patent_doc_id:str):
    values = []
    records = get_spec_embeddings_by_patent_doc_id(patent_doc_id)
    for record in records:
        record_values = records[record]['values']
        values.append(record_values)
    return values
