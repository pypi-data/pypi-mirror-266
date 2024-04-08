import random
import asyncio
import time
from logging import getLogger
from typing import Optional

import numpy as np
from openai import OpenAI, AsyncOpenAI, OpenAIError
import tiktoken

from .data_structures import GeneratedPassage
from .requests_utils import DistributedFixedWindowRateLimiter
from .utils import num_tokens_from_messages

logger = getLogger(__name__)

oai = OpenAI()
async_oai = AsyncOpenAI()


openai_models = [
    'text-embedding-3-large'
]

def num_tokens_from_string(string: str, encoding_name: str = 'cl100k_base') -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def openai_embedding_request_with_retry(model_name, input, backoff_factor=2, backoff_override=None, n_retries=3, **kwargs) -> list[list[float]]:
    """Send a chat completion request to OpenAI with retries."""
    for i in range(1, 1 + n_retries):
        try:
            embeddings = oai.embeddings.create(
                input=input,
                model=model_name,
                **kwargs
            )
            return [e.embedding for e in embeddings.data]
        except OpenAIError as e:
            logger.error(f"OpenAIError: {e}")
            if backoff_override is not None:
                jitter = random.uniform(-0.10, 0.10)
                time.sleep(backoff_override * (1 + jitter))
            else:
                jitter = random.uniform(-0.10, 0.10) 
                time.sleep(backoff_factor**i * (1 + jitter))
            continue
        except Exception as e:
            raise e
    raise Exception(f"Failed to send embedding request to OpenAI after {n_retries} retries.")

async def aopenai_embedding_request_with_retry(model_name, input, backoff_factor=2, backoff_override=None, n_retries=3, **kwargs) -> list[list[float]]:
    """Send a chat completion request to OpenAI with retries."""
    for i in range(1, 1 + n_retries):
        try:
            embeddings = await async_oai.embeddings.create(
                input=input,
                model=model_name,
                **kwargs
            )
            return [e.embedding for e in embeddings.data]
        except OpenAIError as e:
            logger.error(f"OpenAIError: {e}")
            if backoff_override is not None:
                jitter = random.uniform(-0.10, 0.10)
                await asyncio.sleep(backoff_override * (1 + jitter))
            else:
                jitter = random.uniform(-0.10, 0.10) 
                await asyncio.sleep(backoff_factor**i * (1 + jitter))
            continue
        except Exception as e:
            raise e
    raise Exception(f"Failed to send embedding request to OpenAI after {n_retries} retries.")

class RankingModel:
    def __init__(self, model):
        self.model_name = model
        if self.model_name not in openai_models:
            raise ValueError(f'Invalid model name: {model}')

    def encode(self, chunks: list[str] | str):
        if self.model_name in openai_models:
            if isinstance(chunks, str):
                chunks = [chunks]
            return openai_embedding_request_with_retry(self.model_name, chunks, dimensions=256)
        
    async def aencode(self, chunks: list[str] | str):
        if self.model_name in openai_models:
            if isinstance(chunks, str):
                chunks = [chunks]
            return await aopenai_embedding_request_with_retry(self.model_name, chunks, dimensions=256)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def find_most_similar_chunks(embeddings: np.ndarray, ref: np.ndarray):
    similarities: list[np.ndarray] = []
    for embedding in embeddings:
        similarities.append(cosine_similarity(ref, embedding))

    similarities = np.vstack(similarities).reshape(-1)
    return np.argsort(similarities)[::-1]

def rank_passages(passages: list[GeneratedPassage], claim_element: str, ranking_model_version: str):
    """
    Mutates the ranking attribute of each passage in the list
    """
    model = RankingModel(ranking_model_version)
    claim_element_embedding = model.encode(claim_element)
    passage_embeddings = model.encode([passage.text for passage in passages])
    sorted_indices = find_most_similar_chunks(passage_embeddings, claim_element_embedding)
    
    for i, sorted_idx in enumerate(sorted_indices):
        passages[sorted_idx].ranking = i + 1
        passages[sorted_idx].ranking_model_version = ranking_model_version

    return passages

async def arank_passages(passages: list[GeneratedPassage], claim_element: str, ranking_model_version: str):
    """
    Mutates the ranking attribute of each passage in the list
    """
    model = RankingModel(ranking_model_version)
    claim_element_embedding = model.encode(claim_element)
    passage_embeddings = await model.aencode([passage.text for passage in passages])
    sorted_indices = find_most_similar_chunks(passage_embeddings, claim_element_embedding)
    
    for i, sorted_idx in enumerate(sorted_indices):
        passages[sorted_idx].ranking = i + 1
        passages[sorted_idx].ranking_model_version = ranking_model_version

    return passages