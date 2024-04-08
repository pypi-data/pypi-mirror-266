import math
from typing import Callable

import numpy as np


def lcs_length(seq1: list[str], seq2: list[str]):
    """
    Longest common substring length
    """
    L = np.array([[0 for _ in range(len(seq2) + 1)] for _ in range(len(seq1) + 1)])
    z = 0
    for i in range(1, len(seq1) + 1):
        for j in range(1, len(seq2) + 1):
            if seq1[i - 1] == seq2[j - 1]:
                L[i, j] = L[i - 1, j - 1] + 1
                if L[i, j] > z:
                    z = L[i, j]
            else:
                L[i, j] = 0

    return z

def lcs(seq1: list[str], seq2: list[str]):
    """
    Longest common substring
    """
    L = np.array([[0 for _ in range(len(seq2) + 1)] for _ in range(len(seq1) + 1)])
    lcs_s: set[tuple[str, ...]] = set()
    z = 0
    for i in range(1, len(seq1) + 1):
        for j in range(1, len(seq2) + 1):
            if seq1[i - 1] == seq2[j - 1]:
                L[i, j] = L[i - 1, j - 1] + 1
                if L[i, j] > z:
                    z = L[i, j]
                    lcs_s.clear()
                    lcs_s.add(tuple(seq1[i - z:i]))
                elif L[i, j] == z:
                    lcs_s.add(tuple(seq1[i - z:i]))
            else:
                L[i, j] = 0


    return lcs_s

def default_hit_predicate(hyp: list[str], ref: list[str], hit_length: int = 10):
    return lcs_length(hyp, ref) > min(hit_length, len(ref))

def calculate_hit_rate(claim_element: tuple[float, str], selected_passages: list[str], reference: dict[tuple[float, str], list[str]], hit_predicate: Callable = default_hit_predicate):
    claim_element_text, reference_passages = reference.get(claim_element[0])

    selected_passages = [i.strip().split() for i in selected_passages]
    reference_passages = [i[0].strip().split() for i in reference_passages]

    hits = 0
    for reference_passage in reference_passages:
        for selected_passage in selected_passages:
            if hit_predicate(selected_passage, reference_passage):
                hits += 1
                break

    return hits / len(reference_passages)

def get_matching_passages(claim_element: tuple[float, str], selected_passages: list[str], reference: dict[tuple[float, str], list[str]], hit_predicate: Callable = default_hit_predicate):
    claim_element_text, reference_passages = reference.get(claim_element[0])
    selected_passages = [i.strip().split() for i in selected_passages]
    reference_passages = [i[0].strip().split() for i in reference_passages]

    matching_passages = []
    for reference_passage in reference_passages:
        for selected_passage in selected_passages:
            if hit_predicate(selected_passage, reference_passage):
                matching_passages.append((selected_passage, reference_passage))
                break
    
    return matching_passages