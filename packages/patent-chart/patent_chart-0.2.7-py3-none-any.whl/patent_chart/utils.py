from logging import getLogger

import numpy as np
import tiktoken

logger = getLogger(__name__)

def wer_tabular(hyp: list[str], ref: list[str]):
    table = np.zeros((len(hyp) + 1, len(ref) + 1), dtype=np.uint8)
    table[:, 0] = np.arange(len(hyp) + 1)
    table[0, :] = np.arange(len(ref) + 1)

    for i in range(1, len(hyp) + 1):
        for j in range(1, len(ref) + 1):
            table[i, j] = min(
                table[i - 1, j] + 1,
                table[i, j - 1] + 1,
                table[i - 1, j - 1] + (0 if hyp[i - 1] == ref[j - 1] else 1)
            )

    return table[-1, -1]

def calculate_wer(hyp: list[str], ref: list[str]):
    word_error_count = wer_tabular(hyp, ref)
    return word_error_count / len(ref)


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
  """Returns the number of tokens used by a list of messages."""
  try:
      encoding = tiktoken.encoding_for_model(model)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  if model == "gpt-3.5-turbo-0613":  # note: future models may deviate from this
      num_tokens = 0
      for message in messages:
          num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  # if there's a name, the role is omitted
                  num_tokens += -1  # role is always required and always 1 token
      num_tokens += 2  # every reply is primed with <im_start>assistant
      return num_tokens
  else:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
  See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")