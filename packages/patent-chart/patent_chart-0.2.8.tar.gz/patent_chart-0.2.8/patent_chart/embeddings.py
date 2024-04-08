import pickle
from dataclasses import dataclass
import numpy as np

from sentence_transformers import SentenceTransformer

from patent_chart.parser import PatentTextLine, serialize_chunk

def get_model(model_name):
    if model_name == 'instructor-xl':
        return SentenceTransformer('hkunlp/instructor-xl')
    elif model_name == 'all-MiniLM-L6-v2':
        return SentenceTransformer('all-MiniLM-L6-v2')

def load_embeddings_from_pickle_dump(embeddings_path):
    with open(embeddings_path, "rb") as fIn:
        return pickle.load(fIn)
    
def save_spec_chunk_embeddings(spec_chunk_embeddings, embeddings_path):
    with open(embeddings_path, "wb") as fOut:
        pickle.dump(spec_chunk_embeddings, fOut, protocol=pickle.HIGHEST_PROTOCOL)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def find_most_similar_chunks(embeddings, summary_plus_claim_embedding, n=10):
    similarities = []
    for embedding in embeddings:
        similarities.append(cosine_similarity(summary_plus_claim_embedding, embedding))

    similarities = np.vstack(similarities).reshape(-1)
    return np.argsort(similarities)[-n:]

@dataclass
class EmbeddedSpec:
    paragraphs: list[list[PatentTextLine]]
    embeddings: list[np.ndarray]

def select_passages_for_claim_element(patent_summary_embedding: np.ndarray, patent_claim_element_embedding: np.ndarray, prior_art_spec: EmbeddedSpec, n_passages=10):
    claim_element_embedding = patent_claim_element_embedding.reshape(1, -1)
    most_similar_chunk_indices = find_most_similar_chunks(prior_art_spec.embeddings, claim_element_embedding + patent_summary_embedding, n=n_passages)
    selected_passages = []
    for i in most_similar_chunk_indices:
        selected_passages.append(serialize_chunk(prior_art_spec.paragraphs[i]))

    return selected_passages