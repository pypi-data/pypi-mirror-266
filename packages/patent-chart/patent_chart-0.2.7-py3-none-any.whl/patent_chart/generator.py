import re
import os
import time
import asyncio
import uuid
import random
from logging import getLogger
from dataclasses import dataclass
from typing import Callable, Optional, AsyncIterator, Coroutine, List
from functools import partial, lru_cache

from openai import OpenAI, AsyncOpenAI, OpenAIError
import tiktoken
from anthropic import AsyncAnthropic
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

from . import parser
from . import ranking
from . import search_index
from .utils import num_tokens_from_messages
from .data_structures import GeneratedPassage
from .requests_utils import DistributedFixedWindowRateLimiter

logger = getLogger(__name__)

oai = OpenAI()
async_oai = AsyncOpenAI()

ac = AsyncAnthropic()

class GenerationError(Exception):
    pass

RATE_LIMIT_INTERVAL = 60  # seconds

# OpenAI text-embedding-3-large
MAX_SEQ_LENGTH = 8191

# rate limit
token_rate_limit_by_model_name = {
    'gpt-4': 300_000,
    'gpt-3.5-turbo': 2_000_000,
    'gpt-3.5-turbo-16k': 2_000_000,
    'gpt-3.5-turbo-instruct': 250_000,
    'gpt-3.5-turbo-0125': 2_000_000,
    'gpt-4-turbo-preview': 600_000,
    'claude-3-opus-20240229': 400_000,
}

# context window
model_name_to_token_limit = {
    'gpt-4': 8192,
    'gpt-3.5-turbo-16k': 16384,
    'gpt-3.5-turbo': 4096,
    'gpt-3.5-turbo-16k-0613': 16384,
    'gpt-3.5-turbo-0125': 16385,
    'gpt-4-turbo-preview': 128_000,
    'claude-3-opus-20240229': 200_000,
}


def prompt_claim_element_only(claim_element, prior_art_passage, n_passages_per_split=3):
    messages = [
        {"role": "system", "content": f"You work for a law firm. Your task is to interpret a single claim element that I select from the claims of a patent. Then I'm going to give you a passage from the prior art and you need to pick {n_passages_per_split} distinct sub-passages from the passage that you believe are the most similar to the claim element. Please output only those {n_passages_per_split} passages, copied verbatim from the prior art. Do not add any other text besides the verbatim passages."},
        {"role": "user", "content": f"Selected claim element: {claim_element}"},
        {"role": "user", "content": f"Prior art passage: {prior_art_passage}"},
    ]
    return messages

def prompt_summary_full_set_of_claims(summary, claims, claim_element, prior_art_passage, n_passages_per_split=3):
    messages = [
        {"role": "system", "content": f"You work for a law firm. Your task is to read the summary of the written description of a patent and the full set of claims in the patent and interpret a single claim element that I select from the claims of the patent in light of the summary and the full set of claims. Then I'm going to give you a passage from the prior art and you need to pick{n_passages_per_split} distinct sub-passages from the passage that you believe are the most similar to the claim element. Please output only those {n_passages_per_split} passages, copied verbatim from the prior art, each separated by a single newline. Do not add any other text besides the verbatim passages. If you don't believe there are any sub-passages that are similar to the claim element, please output 'None'."},
        {"role": "user", "content": f"Summary of the written description of the invention: {summary}\n\nFull set of claims: {claims}\n\nSelected claim element: {claim_element}Prior art passage: {prior_art_passage}"},
    ]
    return messages


def prompt_full_spec_full_set_of_claims(full_spec, claims, claim_element, prior_art_passage, n_passages_per_split=3):
    messages = [
        {"role": "system", "content": f"You work for a law firm. Your task is to read the the written description of a patent and the full set of claims in the patent and interpret a single claim element selected from the claims of the patent in the context of the written description and the other claim elements. Then I'm going to give you a prior art document and you need to pick up to {n_passages_per_split} distinct passages from the prior art document that you believe are the most similar to the claim element. Please output only those {n_passages_per_split} passages, copied verbatim from the prior art document, each separated by a single '\n'. Do not add any other text besides the verbatim passages. If you don't believe there are any passages that are similar to the claim element, please output 'None'."},
        {"role": "user", "content": f"Written description from the patent: {full_spec} \n\nFull set of claims from the patent: {claims} \n\nSelected claim element from the claims of the patent: {claim_element} \n\nPrior art document: {prior_art_passage}"},
    ]
    return messages


def post_process_selected_passage_gpt4(passage: str) -> list[str]:
    split_strategies = [
        lambda passage: re.split(r'\d+\.', passage),
        lambda passage: passage.split('\n\n'),
        lambda passage: passage.split('\"\n'),
    ]
    for split_strategy in split_strategies:
        split_passages = split_strategy(passage)
        if len(split_passages) > 1:
            break
    # strip newlines, quotes, and whitespace from beginning and end
    split_passages = [p.strip().strip('"') for p in split_passages]
    # filter whitespace only and empty string entries
    split_passages = [p for p in split_passages if p != '']
    # filter out passages that are just a newline
    split_passages = [p for p in split_passages if p != '\n']
        
    return split_passages


def post_process_selected_passage_claude_opus(passage: str) -> list[str]:
    passage = passage.split(':')[-1]
    
    split_strategies = [
        lambda passage: passage.split('\n'),
    ]
    for split_strategy in split_strategies:
        split_passages = split_strategy(passage)
        if len(split_passages) > 1:
            break
    # strip newlines, quotes, and whitespace from beginning and end
    split_passages = [p.strip().strip('"') for p in split_passages]
    # filter whitespace only and empty string entries
    split_passages = [p for p in split_passages if p != '']
    # filter out passages that are just a newline
    split_passages = [p for p in split_passages if p != '\n']
    
    return split_passages
  

def post_process_summary_claude_opus(summary: str) -> str:
    summary = summary.split(':')[-1]
    return summary.strip().strip('"')


@dataclass
class GeneratorConfig:
    model_name: str = 'gpt-4'
    target_n_passages: int = 10
    min_n_splits: int = 1

def load_generator_config_from_env():
    model_name = os.environ.get('LLM_MODEL_NAME', 'gpt-4')
    if model_name not in token_rate_limit_by_model_name:
        raise ValueError(f"Model name {model_name} not recognized.")
    target_n_passages = int(os.environ.get('LLM_TARGET_N_PASSAGES', 10))
    min_n_splits = int(os.environ.get('LLM_MIN_N_SPLITS', 1))
    
    logger.info('Loaded generator config: \n %s \n', )

    config = GeneratorConfig(
        model_name=model_name,
        target_n_passages=target_n_passages,
        min_n_splits=min_n_splits,
    )

    logger.info('Loaded generator config: \n %s \n', config)

    return config

def num_tokens_in_text(text, model="gpt-3.5-turbo-0613"):
  """Returns the number of tokens in a string."""
  try:
      encoding = tiktoken.encoding_for_model(model)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  return len(encoding.encode(text))


def concatenate_completions_for_reranking(completions):
    # concatenate completions and renumber
    # TODO: make 3 a parameter
    concatenated_completions = ''
    for i, completion in enumerate(completions):
        completion_content = completion['choices'][0]['message']['content']
        completion_content1, completion_content = completion_content.split('\n2.')
        completion_content1 = completion_content1.lstrip('1. ')
        completion_content2, completion_content = completion_content.split('\n3.')
        completion_content3 = completion_content
        
        concatenated_completions += f'{int_to_roman(i*3 + 1)}. {completion_content1}\n'
        concatenated_completions += f'{int_to_roman(i*3 + 2)}. {completion_content2}\n'
        concatenated_completions += f'{int_to_roman(i*3 + 3)}. {completion_content3}\n'
    return concatenated_completions, 3 * len(completions)

# Reranking utility functions
def int_to_roman(n: int) -> str:
    if not (0 < n < 4000):
        raise ValueError("Input integer must be between 1 and 3999")
    
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD', 'C', 'XC','L','XL','X','IX','V','IV','I')
    result = []
    
    for i in range(len(ints)):
        count = int(n / ints[i])
        result.append(nums[i] * count)
        n -= ints[i] * count
    
    return ''.join(result)

# parse reranked completions
def parse_reranked_completions(reranked_completion, n_completions):
    # First lstrip prelude before 1.
    # Find index of '1. ' and slice
    reranked_completion = reranked_completion[reranked_completion.index('1. '):]
    
    # Split on i. for i in range(1, n_completions + 1)
    # Then lstrip roman numeral and period
    roman_numeral_regex_pattern = r''
    for i in range(1, n_completions + 1):
        roman_numeral_regex_pattern += f'{int_to_roman(i)}\. '
        if i < n_completions:
            roman_numeral_regex_pattern += '|'
    roman_numeral_regex = re.compile(roman_numeral_regex_pattern)
    
    parsed_completions = []
    for i in range(1, n_completions + 1):
        if i == n_completions:
            parsed_completion = reranked_completion
        else:
            parsed_completion, reranked_completion = reranked_completion.split(f'{i+1}. ', maxsplit=1)
        if i == 1:
            parsed_completion = parsed_completion.lstrip('1. ')
        parsed_completion = re.sub(roman_numeral_regex, '', parsed_completion)
        parsed_completion = parsed_completion.lstrip(' "')
        parsed_completion = parsed_completion.rstrip(' \n"')
        parsed_completions.append(parsed_completion)
        
    return parsed_completions


def openai_prompt_select_passages_from_prior_art_portion(all_but_claims, claims, claim_element, prior_art_passage):
    # TODO: make 3 a parameter
    messages = [
        {"role": "system", "content": "You are an associate at a big law firm. Your task is to read the written description and of an invention disclosed in a patent and the full set of claims in the patent and interpret a single claim element that I select from the claims of the patent in light of the written description and the full set of claims. Then I'm going to give you a passage from of prior art and you need to pick three distinct sub-passages from the passage that you believe are the most semantically similar to the claim element interpreted in light of the written description and the full set of claims. Please output only those three passages, each preceded only by the numberings 1., 2., and 3. and a space."},
        {"role": "user", "content": f"Written description of invention: {all_but_claims}"},
        {"role": "user", "content": f"Full set of claims: {claims}"},
        {"role": "user", "content": f"Selected claim element: {claim_element}"},
        {"role": "user", "content": f"Prior art passage: {prior_art_passage}"},
    ]
    return messages

def openai_prompt_rank_selected_passages(all_but_claims, claims, claim_element, chosen_prior_art_passage, n_completions):
    messages = [
        {"role": "system", "content": f"Your task is to read the written description and of an invention disclosed in a patent and the full set of claims in the patent and interpret a single claim element that I select from the claims of the patent in light of the written description and the full set of claims. Then I'm going to give you {n_completions} sub-passages from the prior art passage i presented to you that you chose because they were the most semantically similar to the selected claim element interpreted in light of the written description and the full set of claims. Please rank these {n_completions} passages in descending order of similarity to the selected claim element interpreted in light of the written description and the full set of claims. I will give you passages numbered by roman numerals, for example: 'I. Passage One... II. Passage two... III. Passage three...'. Please output only the integer ranking following by the roman numeral and passage, for example: '1. II. Passage two ... 2. I. Passage one... 3. III Passage three...' if you believe the ranking should be passage two > passage one > passage three."},
        {"role": "user", "content": f"Written description of invention: {all_but_claims}"},
        {"role": "user", "content": f"Claim element: {claim_element}"},
        {"role": "user", "content": f"Prior art passages to rank: {chosen_prior_art_passage}"},
    ]
    return messages

def openai_chat_completion_request_with_retry(model_name, messages, backoff_factor=2, backoff_override=None) -> str:
    for i in range(1, 3):
        try:
            completion = oai.chat.completions.create(
                model=model_name,
                messages=messages
            )
            return completion.choices[0].message.content
        except OpenAIError as e:
            if backoff_override is not None:
                time.sleep(backoff_override)
            else:
                time.sleep(backoff_factor**i)
            continue
        except Exception as e:
            raise e
    raise Exception("Failed to send chat completion request to OpenAI after 4 retries.")


async def aopenai_chat_completion_request_with_retry(model_name, messages, backoff_factor=2, backoff_override=None, n_retries=3, rate_limiter: Optional[DistributedFixedWindowRateLimiter] = None, **kwargs) -> str:
    """Send a chat completion request to OpenAI with retries."""
    for i in range(1, 1 + n_retries):
        try:
            if rate_limiter is not None:
                num_tokens_in_messages = num_tokens_from_messages(messages)
                # NOTE: separating wait for tokens, the request, and removing tokens is prone to race conditions. We can tolerate occasionally making requests that receive rate limit errors so long as we retry them with backoff.
                if await rate_limiter.wait_for_tokens(num_tokens_in_messages):
                    completion = await async_oai.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        **kwargs
                    )
                    n_tokens_in_completion = completion.usage.completion_tokens
                    await rate_limiter.remove_tokens(n_tokens_in_completion)
            else:
                completion = await async_oai.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    **kwargs
                )
            return completion.choices[0].message.content
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
    raise Exception(f"Failed to send chat completion request to OpenAI after {n_retries} retries.")


def split_passage_to_meet_model_token_limit(passage: str, prompt_func: Callable[[str], list[dict]], model_name: str, min_n_splits: int = 1) -> list[str]:
    """ 
    Given a passage string, a prompt func that takes only the passage string, and a model, find the smallest number of splits necessary to get messages under token limit and return splits of the passage.
    """
    token_limit = model_name_to_token_limit[model_name]
    min_split_size = 256
    # We use cl100k_base as the tokenizer for estimating even for Claude which has a closed-source tokenizer.
    base_num_tokens = num_tokens_from_messages(
        prompt_func(' ' * min_split_size)
    )
    if base_num_tokens > token_limit:
        raise GenerationError("Prompt exceeds token limit by itself.")
    
    passage_splits = []
    passage_split_count = min_n_splits
    while True:
        # Check all splits
        candidate_splits = []
        for i in range(passage_split_count):
            if i == 0:
                candidate_split = passage[:len(passage) // passage_split_count]
            else:
                candidate_split = passage[len(passage) // passage_split_count * i:len(passage) // passage_split_count * (i+1)]
            candidate_splits.append(candidate_split)
        num_tokens = [num_tokens_from_messages(prompt_func(split)) for split in candidate_splits]
        if all([n <= token_limit - 0.05 * token_limit for n in num_tokens]):
            passage_splits = candidate_splits
            break
        passage_split_count += 1

    return passage_splits


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True)
async def aclaude_chat_completion_request(model_name, messages) -> str:
    system_message = messages.pop(0)
    completion = await ac.messages.create(
        max_tokens=4096,
        system=system_message['content'],
        messages=messages,
        model=model_name,
    )
    print(completion)
    return completion.content[0].text


def make_get_completion_coro(model_name, messages, rate_limiter=None):
    if model_name == 'gpt-4':
        return aopenai_chat_completion_request_with_retry(model_name, messages, rate_limiter=rate_limiter)
    elif model_name == 'claude-3-opus-20240229':
        return aclaude_chat_completion_request(model_name, messages)


async def agenerate_passages_for_prior_art_splits(prior_art_splits: list[str], prompt_func: Callable[[str], list[dict]], model_name: str, claim_element_id: int, prior_art_id: int, rate_limiter: Optional[DistributedFixedWindowRateLimiter] = None) -> list[GeneratedPassage | Exception]:
    # make parallel requests to openai api for prior art splits
    passages: list[GeneratedPassage | Exception] = []
    coros = []
    for prior_art_split in prior_art_splits:
        messages = prompt_func(prior_art_split)
        coros.append(make_get_completion_coro(model_name, messages, rate_limiter=rate_limiter))
        
    completions = await asyncio.gather(*coros, return_exceptions=True)
    for i, completion in enumerate(completions):
        if isinstance(completion, Exception):
            print(f'Failed to get completion for prior art split {i} of prior art {prior_art_id} for claim element {claim_element_id}')
            print(completion)
            passages.append(completion)
        else:
            selected_passages = completion
            if model_name == 'gpt-4':
                post_process_generated_passages_func = post_process_selected_passage_gpt4
            elif model_name == 'claude-3-opus-20240229':
                post_process_generated_passages_func = post_process_selected_passage_claude_opus
            else:
                raise NotImplementedError(f"Post processing function for model {model_name} not implemented.")
            
            post_processed_passages = post_process_generated_passages_func(selected_passages)

            for processed_passage in post_processed_passages:
                # We'll add the start line and end line later
                passages.append(
                    GeneratedPassage(
                        prior_art_source_id=prior_art_id,
                        text=processed_passage,
                        claim_element_id=claim_element_id,
                        model_id=model_name
                    )
                )

    passages = [p for p in passages if not isinstance(p, Exception)]

    return passages


async def agenerate_passages(claim_elements: list[tuple[int, str]], prior_art: tuple[int, str], prompt_func: Callable[[str], list[dict]], model_name: str, target_n_passages: int = 10, min_n_splits:int = 1, rate_limiter: Optional[DistributedFixedWindowRateLimiter] = None) -> AsyncIterator[tuple[int, tuple[int, list[str]]]]:
    tasks = []
    for i, claim_element in claim_elements:
        prior_art_splits = split_passage_to_meet_model_token_limit(prior_art[1], partial(prompt_func, claim_element), model_name, min_n_splits=min_n_splits)
        n_passages_per_split = max(target_n_passages // len(prior_art_splits), 1)
        tasks.append(asyncio.create_task(
            agenerate_passages_for_prior_art_splits(prior_art_splits, partial(prompt_func, claim_element, n_passages_per_split=n_passages_per_split), model_name, claim_element_id=i, prior_art_id=prior_art[0], rate_limiter=rate_limiter)
        ))
    
    for coro in asyncio.as_completed(tasks):
        yield await coro


def create_generate_passages_tasks(claim_elements: list[tuple[int, str]], prior_art: tuple[int, str], prompt_func: Callable[[str], list[dict]], model_name: str, target_n_passages: int = 10, min_n_splits:int = 1, rate_limiter: Optional[DistributedFixedWindowRateLimiter] = None) -> list[asyncio.Task]:
    tasks = []
    for i, claim_element in claim_elements:
        prior_art_splits = split_passage_to_meet_model_token_limit(prior_art[1], partial(prompt_func, claim_element), model_name, min_n_splits=min_n_splits)
        n_passages_per_split = max(target_n_passages // len(prior_art_splits), 1)
        tasks.append(asyncio.create_task(
            agenerate_passages_for_prior_art_splits(prior_art_splits, partial(prompt_func, claim_element, n_passages_per_split=n_passages_per_split), model_name, claim_element_id=i, prior_art_id=prior_art[0], rate_limiter=rate_limiter)
        ))

    return tasks


def summarize_patent_prompt_func(serialized_patent_spec: str, instruction: str = None):
    if instruction is None:
        instruction = "Summarize the following patent specification in approximately 250 words. Your summary should not mention the 'patent', 'the specification', 'various embodiments', or any other language that suggests the summary is from a patent. You should not prefix the summary with 'Summary:' or any other prefatory language. The summary should be a standalone short paragraph."
    return [
        {"role": "system", "content": f"{instruction}"},
        {"role": "user", "content": f'Here is the specification to summarize: {serialized_patent_spec}'},
    ]


def summarize_summaries_prompt_func(summaries: List[str], instruction: Optional[str] = None):
    if instruction is None:
        instruction = "Summarize the following partial summaries of sequential portions of a patent specification in approximately 250 words. Your summary should not mention the 'patent', 'the specification', 'various embodiments', or any other language that suggests the summary is from a patent. You should not prefix the summary with 'Summary:' or any other prefatory language. The summary should be a standalone short paragraph"
    partial_summaries = '\n'.join(summaries)
    return [
        {"role": "system", "content": f"{instruction}"},
        {"role": "user", "content": f"Here are the sequential partial summaries I'd like you to summarize: {partial_summaries}"},
    ]


def short_summary_prompt_func(summary: str):
    return [
        {"role": "system", "content": "Condense the following summary to approximately 25 words. As an example, here is a long summary: 'The patent specification describes a closed-loop/semi-closed loop therapy modification system for insulin delivery in diabetes patients, focusing on managing over/under-delivery of medication. The system, incorporating a glucose sensor and insulin pump, triggers alarms based on blood glucose levels or insulin delivery discrepancies, prompting calibration of the sensor system and adjustments to therapy delivery parameters. The system aims to achieve and maintain target blood glucose levels effectively.\n\nThe invention relies on monitoring glucose levels continuously or periodically, adjusting insulin delivery based on the difference between measured and target values. Patient intervention may be required to approve calibration or therapy adjustments. The algorithm limits adjustments within preset boundaries, considering patient's basal pattern. It logs adjustments for patient reference and recommends new basal rates if adjustments consistently reach boundaries.\n\nSafeguards are incorporated to prevent excessive insulin delivery, including safety reviews, real-time calibration adjustment procedures, and safeguards when transitioning from closed-loop to open-loop systems. Additionally, the system accounts for insulin on board delays, ensuring insulin action is adequate before increasing doses. A model supervisory system and tolerance intervals further enhance safety and accuracy in therapy management.\n\nThe specification emphasizes versatility, adaptability, and patient-centric customization, aiming to optimize insulin therapy for diabetes patients. Various embodiments are discussed to address different scenarios and challenges that may arise during insulin delivery, ensuring patient safety and treatment effectiveness throughout the process.' Here is an initial attempt at a condensed summary: 'Description of a closed-loop/semi-closed loop system for insulin delivery in diabetes patients, focusing on managing medication delivery with glucose sensor and insulin pump for optimized therapy results.' Here is a second attempt at a condensed summary: 'Closed-loop/semi-closed loop therapy modification system for insulin delivery in diabetes patients, focusing on managing medication delivery with glucose sensor and insulin pump for optimized therapy results.' This attempt is better because it omits the 'Description of' preamble and focuses exclusively on describing the invention. Your condensed summary should not mention the 'patent', 'the specification', 'various embodiments', or any other language that suggests the summary is from a patent. You should not prefix the summary with 'Summary:' or any other prefatory language. The summary should be a standalone short paragraph or sentence."},
        {"role": "user", "content": f'Here is the long summary for you to summarize: {summary}'},
    ]


def topics_from_summary_prompt_func(summary: str):
    return [
        {"role": "system", "content": "Identify the main topics in the following summary. You may state up to 5 topics in a comma separated list. If you believe there are fewer than 5 topics, you may state fewer. If you believe there are more than 5 topics, you may state the most important 5. Each topic should be one exactly one word. As an example, here is a long summary: 'The patent specification describes a closed-loop/semi-closed loop therapy modification system for insulin delivery in diabetes patients, focusing on managing over/under-delivery of medication. The system, incorporating a glucose sensor and insulin pump, triggers alarms based on blood glucose levels or insulin delivery discrepancies, prompting calibration of the sensor system and adjustments to therapy delivery parameters. The system aims to achieve and maintain target blood glucose levels effectively.\n\nThe invention relies on monitoring glucose levels continuously or periodically, adjusting insulin delivery based on the difference between measured and target values. Patient intervention may be required to approve calibration or therapy adjustments. The algorithm limits adjustments within preset boundaries, considering patient's basal pattern. It logs adjustments for patient reference and recommends new basal rates if adjustments consistently reach boundaries.\n\nSafeguards are incorporated to prevent excessive insulin delivery, including safety reviews, real-time calibration adjustment procedures, and safeguards when transitioning from closed-loop to open-loop systems. Additionally, the system accounts for insulin on board delays, ensuring insulin action is adequate before increasing doses. A model supervisory system and tolerance intervals further enhance safety and accuracy in therapy management.\n\nThe specification emphasizes versatility, adaptability, and patient-centric customization, aiming to optimize insulin therapy for diabetes patients. Various embodiments are discussed to address different scenarios and challenges that may arise during insulin delivery, ensuring patient safety and treatment effectiveness throughout the process.' And this would be an acceptable output: 'Insulin delivery, Diabetes, Therapy system, Monitoring, Glucose sensor'. Topics should reference the specifics of the invention, not the patent or the specification. For example, 'Patent specification' would be an unacceptable topic. Do not include prefatory language such as 'Based on the provided summary, here are the main topics:' or 'The main topics are:', just return the five topics each separated by a comma."},
        {"role": "user", "content": f'Here is the long summary for you to choose topics from: {summary}'},
    ]


def parse_topics(topics: str) -> list[str]:
    topics_list = topics.split(',')
    topics_list = [t.strip(' \'\n') for t in topics_list]
    return topics_list


async def asummarize_patent(patent: parser.GoogleParsedPatent, rate_limiter: Optional[DistributedFixedWindowRateLimiter] = None, generator_config=None):
    if generator_config is None:
        generator_config = load_generator_config_from_env()
    serialized_patent_spec = patent.specification

    split_instruction = "Summarize the following portion of a patent specification in approximately 250 words:"
    spec_splits = split_passage_to_meet_model_token_limit(serialized_patent_spec, partial(summarize_patent_prompt_func, instruction=split_instruction), generator_config.model_name)

    if len(spec_splits) == 1:
        summarization = await make_get_completion_coro(
            generator_config.model_name, summarize_patent_prompt_func(serialized_patent_spec), rate_limiter=rate_limiter
        )
    else:
        tasks = []
        # TODO: hack
        for spec_split in spec_splits[:10]:
            tasks.append(
                make_get_completion_coro(
                    generator_config.model_name, summarize_patent_prompt_func(spec_split, instruction=split_instruction), rate_limiter=rate_limiter
                )
            )
        partial_summaries = await asyncio.gather(*tasks)
        if generator_config.model_name == 'claude-3-opus-20240229':
            partial_summaries = [post_process_summary_claude_opus(partial_summary) for partial_summary in partial_summaries]
        try:
            summarization = await make_get_completion_coro(
                generator_config.model_name, summarize_summaries_prompt_func(partial_summaries), rate_limiter=rate_limiter
            )
        except GenerationError as e:
            logger.error('Failed to summarize patent %s', patent.unique_id)
            summarization = ''

    if generator_config.model_name == 'claude-3-opus-20240229':
        summarization = post_process_summary_claude_opus(summarization)

    short_summary = await make_get_completion_coro(
        generator_config.model_name, short_summary_prompt_func(summarization), rate_limiter=rate_limiter
    )
    if generator_config.model_name == 'claude-3-opus-20240229':
        short_summary = post_process_summary_claude_opus(short_summary)

    topics = await make_get_completion_coro(
        generator_config.model_name, topics_from_summary_prompt_func(summarization), rate_limiter=rate_limiter
    )
    topics = parse_topics(topics)

    search_index.update_patent_by_id(patent, summary=summarization, short_summary=short_summary, topics=topics)

    return summarization


async def asummarize_patents(patents: list[parser.GoogleParsedPatent]):
    generator_config = load_generator_config_from_env()
    async with DistributedFixedWindowRateLimiter(token_rate_limit_by_model_name[generator_config.model_name], RATE_LIMIT_INTERVAL) as rate_limiter:
        tasks = [asummarize_patent(patent, rate_limiter=rate_limiter) for patent in patents]
        return await asyncio.gather(*tasks)


async def asummarize_patents_gpt4_turbo_preview(patents: list[parser.GoogleParsedPatent]):
    generator_config = load_generator_config_from_env()
    generator_config.model_name = 'gpt-4-turbo-preview'
    async with DistributedFixedWindowRateLimiter(token_rate_limit_by_model_name[generator_config.model_name], RATE_LIMIT_INTERVAL) as rate_limiter:
        tasks = [asummarize_patent(patent, rate_limiter=rate_limiter, generator_config=generator_config) for patent in patents]
        return await asyncio.gather(*tasks)


async def hydrate_prompt_with_patent(patent: parser.GoogleParsedPatent, generator_config: GeneratorConfig) -> partial[Callable[[str], list[dict]]]:
    claims = patent[1].claims
    all_patent_claim_elements = []
    for claim in claims:
        all_patent_claim_elements.extend(claim.claim_elements)
    serialized_claims = '\n'.join(all_patent_claim_elements)
    
    if generator_config.model_name == 'gpt-4':
        patent_summary = search_index.get_patent_summary(patent[1])
        if patent_summary is None:
            patent_summary = await asummarize_patent(patent[1])
        prompt_func = partial(prompt_summary_full_set_of_claims, patent_summary, serialized_claims)
        return prompt_func
    elif generator_config.model_name == 'claude-3-opus-20240229':
        return partial(prompt_full_spec_full_set_of_claims, patent[1].specification, serialized_claims)
    else:
        raise NotImplementedError(f"Model {generator_config} not supported.")


async def abulk_generate_passages(
        patent: tuple[int, parser.GoogleParsedPatent], 
        prior_art_sources: list[tuple[int, parser.GoogleParsedPatent]], claim_elements: list[tuple[int, str]],
        ranking_params: dict,
        ) -> AsyncIterator[GeneratedPassage]:
    # TODO: this function should be refactored to separate concerns
    generator_config = load_generator_config_from_env()
    async with DistributedFixedWindowRateLimiter(token_rate_limit_by_model_name[generator_config.model_name], RATE_LIMIT_INTERVAL) as rate_limiter:
        prompt_func = await hydrate_prompt_with_patent(patent, generator_config)
        tasks = []
        for prior_art_source_uid, prior_art_source in prior_art_sources:
            serialized_prior_art_source = prior_art_source.specification
            tasks.extend(
                create_generate_passages_tasks(
                    claim_elements, (prior_art_source_uid, serialized_prior_art_source), 
                    prompt_func,
                    generator_config.model_name,
                    target_n_passages=generator_config.target_n_passages,
                    min_n_splits=generator_config.min_n_splits,
                    rate_limiter=rate_limiter
            ))
        
        for coro in asyncio.as_completed(tasks):
            generated_passages = await coro
            # TODO: once we yield the whole list of generated passages for each awaited task, we can do the ranking step in the caller
            # Find matching claim element
            if generated_passages:
                claim_element_id = generated_passages[0].claim_element_id
                matching_claim_element = [c for c in claim_elements if c[0] == claim_element_id][0]
                if not all([p.claim_element_id == claim_element_id for p in generated_passages]):
                    logger.error('Claim element ids do not match')
                
                logger.info(f'Ranking {len(generated_passages)} passages')
                ranked_generated_passages = await ranking.arank_passages(generated_passages, matching_claim_element[1], **ranking_params)
                for generated_passage in ranked_generated_passages:
                    yield generated_passage


@lru_cache
def num_tokens_from_string(string: str, encoding_name: str = 'cl100k_base') -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True)
def encode_openai(text_batch):
    embeddings = oai.embeddings.create(
        input=text_batch,
        model='text-embedding-3-large',
        dimensions=1024
    )
    return [e.embedding for e in embeddings.data]


def batch_encode_openai(texts):
    i = 0
    embeddings = []
    while i < len(texts):
        batch_tok_count = 0
        batch = []
        while i < len(texts) and batch_tok_count + num_tokens_from_string(texts[i]) < MAX_SEQ_LENGTH:
            batch_tok_count += num_tokens_from_string(texts[i])
            batch.append(texts[i])
            i += 1
        embeddings.extend(encode_openai(batch))
        
    return embeddings