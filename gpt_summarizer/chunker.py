from cornsnake import util_print
from typing import Generator

from . import config


def _divide_into_chunks(list: list[str], size: int) -> Generator[list[str], None, None]:
    for i in range(0, len(list), size):
        yield list[i : i + size]


def chunk_text_by_words(input_text: str) -> list[str]:
    input_words = input_text.split(" ")
    input_words_count = len(input_words)
    input_text_list: list[str] = []

    if input_words_count > config.MAIN_INPUT_WORDS:
        util_print.print_warning(
            f"The input file has many words! Max is {config.MAIN_INPUT_WORDS} but that file has {input_words_count} words. Will chunk the text."
        )
        chunks = _divide_into_chunks(input_words, config.MAIN_INPUT_WORDS)
        input_text_list = []
        for chunk in chunks:
            input_text_list.append(" ".join(chunk))
        print(f"Split into {len(input_text_list)} chunks")
    else:
        input_text_list = [input_text]
    return input_text_list
