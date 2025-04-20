import semchunk
from cornsnake import util_print

from . import config


def _remove_empty_chunks(chunks: list[str]) -> list[str]:
    def _has_alphanumeric(text: str) -> bool:
        return any(char.isalnum() for char in text)

    return list(filter(_has_alphanumeric, chunks))


def _divide_into_chunks(
    input_text: str, chunk_size_in_tokens: int, overlap_ratio: float
) -> list[str]:
    # - need some overlap, to help deal with split sentences
    chunker = semchunk.chunkerify(
        lambda text: len(text.split()), chunk_size=chunk_size_in_tokens
    )
    chunks = chunker(input_text, processes=2, overlap=overlap_ratio)
    chunks_list: list[str] = []

    for chunk in chunks:
        if isinstance(chunk, str):
            chunks_list.append(chunk)
        else:
            raise NotImplementedError(f"Chunk should be str: {chunk}")

    return _remove_empty_chunks(chunks=chunks_list)


def chunk_text_by_words(input_text: str) -> list[str]:
    input_words = input_text.split(" ")
    input_words_count = len(input_words)
    chunk_list: list[str] = [input_text]

    if input_words_count > config.CHUNK_SIZE_IN_WORDS:
        util_print.print_warning(
            f"The input file has many words! Max is {config.CHUNK_SIZE_IN_WORDS} but that file has {input_words_count} words. Will chunk the text."
        )
        # TODO (someone): should convert chunk size from words -> tokens
        chunk_list = _divide_into_chunks(
            input_text=input_text,
            chunk_size_in_tokens=config.CHUNK_SIZE_IN_WORDS,
            overlap_ratio=config.CHUNK_OVERLAP_RATIO,
        )

        if config.is_debug:
            for i, chunk in enumerate(chunk_list):
                util_print.print_section(f"Chunk:{i}")
                print(chunk)

        util_print.print_important(f"Split into {len(chunk_list)} chunks")

    return chunk_list
