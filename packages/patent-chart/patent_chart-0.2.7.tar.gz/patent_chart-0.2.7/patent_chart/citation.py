from logging import getLogger

from . import parser
from .utils import calculate_wer

logger = getLogger(__name__)

class CitationError(Exception):
    pass

def cite_passage(passage: str, patent: parser.ParsedPatent) -> tuple[parser.PatentTextLine, parser.PatentTextLine]:
    """
    Given a serialized passage that came from the document, convert the passage back into a list of parser.PatentTextLine objects, then return the two PatentTextLine objects marking the beginning and end of the passage, inclusive on both ends.

    The serialized specification should have been constructed using parser.serialized_specification_from_parsed_patent which returns a list of strings and then joined with "\n" to create a string. So splitting the selected passage on should recover the list of strings that can then be matched against the list of patent text lines in the parsed patent.
    """
    patent_text_lines = patent.text_lines

    # Split the passage into lines
    # passage_lines = passage.split('\n')
    # if len(passage_lines) > 1:
    #     def find_matching_line(line: str) -> parser.PatentTextLine | None:
    #         for patent_text_line in patent_text_lines.column_0:
    #             # This is kind of a hack and probably not very robust
    #             if patent_text_line.text.startswith(line):
    #                 return patent_text_line
    #         for patent_text_line in patent_text_lines.column_1:
    #             # This is kind of a hack and probably not very robust
    #             if patent_text_line.text.startswith(line):
    #                 return patent_text_line
    #         # Currently shouldn't get here, but just in case
    #         for patent_text_line in patent_text_lines.noncolumnar:
    #             # This is kind of a hack and probably not very robust
    #             if patent_text_line.text.startswith(line):
    #                 return patent_text_line
    #         return None
        
    #     start_line = find_matching_line(passage_lines[0])

    #     if start_line is None:
    #         raise CitationError(f"Could not find start line for passage: {passage}")
        
    #     end_line = find_matching_line(passage_lines[-1])

    #     if end_line is None:
    #         raise CitationError(f"Could not find end line for passage: {passage}")
        
    #     return (start_line, end_line)
    # else:

    best_passage = []
    best_wer = 1.0
    logger.info(f'Citing passage: {passage}')
    passage_words = passage.split()
    patent_words = parser.flatten_parsed_patent_to_words(patent)
    for i, patent_word in enumerate(patent_words):
        # We assume the first word in the passage returned by the language model will always be a well-formed word that exists in the patent. I.e., it won't be a word fragment, like the hyphenated part of a word. If it is, it probably matches a word in the parsed patent anyway because that's probably where the language model got that from.
        if patent_word.text == passage_words[0]:
            candidate_passage = patent_words[i:i+len(passage_words)]
            wer = calculate_wer([w.text for w in candidate_passage], passage_words)
            if wer < best_wer:
                best_wer = wer
                best_passage = candidate_passage
    if best_passage:
        return (best_passage[0].line, best_passage[-1].line)
    
    raise CitationError(f"Could not find start line for passage: {passage}")