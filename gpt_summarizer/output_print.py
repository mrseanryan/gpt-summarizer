from cornsnake import (
    util_print,
    util_time,
)

from . import config


def print_final_result(
    files_processed: int,
    elapsed_seconds: float,
    files_skipped: int,
    cost: float,
    files_bad: int,
) -> None:
    util_print.print_section("Completed")
    util_print.print_result(
        f"{files_processed} files processed in {util_time.describe_elapsed_seconds(elapsed_seconds)}"
    )
    if files_skipped > 0:
        util_print.print_result(
            f"{files_skipped} files skipped (output already exists)"
        )
    if files_bad > 0:
        util_print.print_warning(f"{files_bad} bad files skipped")
    if cost > 0:
        util_print.print_important(
            f" -- Total estimated cost: {config.OPENAI_COST_CURRENCY}{cost}"
        )


def print_file_result(
    title: str,
    short_summary: str,
    long_summary: str,
    paragraphs: list[str],
    elapsed_seconds: float,
    cost: float,
    chunk_count: int,
    chunks_failed: int,
) -> None:
    util_print.print_section(f"TITLE: {title}")

    util_print.print_section("FULL Short Summary")
    print(short_summary)

    util_print.print_section("FULL Long Summary")
    print(long_summary)

    if paragraphs:
        util_print.print_section("FULL paragraphs Summary")
        print("\n".join(paragraphs))

    util_print.print_result(
        f" -- THIS FILE time: {util_time.describe_elapsed_seconds(elapsed_seconds)}"
    )
    util_print.print_important(f" -- THIS FILE chunks: {chunk_count}")

    if cost > 0.0:
        util_print.print_important(
            f" -- THIS FILE estimated cost: {config.OPENAI_COST_CURRENCY}{cost}"
        )
    if chunks_failed > 0:
        util_print.print_warning(
            f"{chunks_failed} of {chunk_count} document chunks were skipped. If the summary is not of high quality, you can re-run with smaller chunks, by reducing CHUNK_SIZE_IN_WORDS in config.py."
        )
