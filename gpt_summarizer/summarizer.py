import os
from typing import Any, Tuple

from cornsnake import (
    util_file,
    util_dir,
    util_print,
)

from . import chunker
from . import config
from . import extractor
from . import llm_caller
from . import llm_response_helper
from . import output_file
from . import output_print
from . import prompts
from . import util_config


def _round_cost(cost: float) -> float:
    return round(cost, config.OPENAI_COST__DECIMALS)


def _extract_text_to_chunks(path_to_input_file: str) -> list[str]:
    input_text = extractor.extract_text(path_to_input_file)
    return chunker.chunk_text_by_words(input_text)


def _summarize_one_file(
    path_to_input_file: str,
    target_language: str | None,
    path_to_output_dir: str | None,
    original_path_to_input_file_or_dir_or_url: str,
    path_to_move_done_files_dir: str | None,
) -> Tuple[float, float]:  # (elapsed_seconds, cost)
    util_print.print_section(f"Summarizing '{path_to_input_file}'")

    input_text_chunks = _extract_text_to_chunks(path_to_input_file)

    if target_language is None:
        print(f"Summarizing file at '{path_to_input_file}'...")
    else:
        print(f"Summarizing file at '{path_to_input_file}' into {target_language}...")

    title = ""
    short_summary = ""
    long_summary = ""
    paragraphs: list[str] = []
    elapsed_seconds = 0.0
    cost = 0.0

    chunks_failed = 0
    chunk_count = 1
    for text in input_text_chunks:
        prompt = ""
        rsp: dict[str, Any] | None = None
        if util_config.is_local_via_ctransformers():
            # TODO try fix
            if target_language is not None:
                raise RuntimeError(
                    "target_language is only supported when using Open AI ChatGPT"
                )
            prompt = prompts.get_simple_summarize_prompt(text)
            if config.LOCAL_CTRANSFORMERS_MODEL_TYPE == "llama":
                prompt = prompts.get_llama_summarize_prompt(text)
            (response_plain, _elapsed_seconds, _cost) = (
                llm_caller.send_to_llm_with_retry(prompt)
            )
            elapsed_seconds += _elapsed_seconds
            rsp = {"short_summary": response_plain}
        elif util_config.is_local_via_ollama():
            if target_language is None:
                prompt = prompts.get_ollama_summarize_prompt(text)
            else:
                prompt = prompts.get_ollama_summary_prompt_and_translate_to(
                    text, target_language
                )
            (rsp, _elapsed_seconds, _cost) = llm_caller.send_to_llm_with_retry(prompt)
            elapsed_seconds += _elapsed_seconds
            cost += _cost
        elif util_config.is_openai():
            if target_language is None:
                prompt = prompts.get_chatgpt_summarize_prompt(text)
            else:
                prompt = prompts.get_chatgpt_summarize_prompt_and_translate_to(
                    text, target_language
                )
            (rsp, _elapsed_seconds, _cost) = llm_caller.send_to_llm_with_retry(prompt)
            elapsed_seconds += _elapsed_seconds
            cost += _cost
        else:
            raise ValueError(
                "Please check config.py - one of openai, local via ctransformers OR ollama should be enabled."
            )

        util_print.print_section(
            f"Short Summary = Chunk {chunk_count} of {len(input_text_chunks)}"
        )
        if rsp is None:
            chunks_failed += 1
        else:
            if isinstance(rsp, str):
                util_print.print_warning("Response is string - expected dict")
                print(rsp)
                short_summary += rsp + "\n"
            else:
                rsp_title_in_quotes = rsp.get("title_in_quotes", None)
                if rsp_title_in_quotes:
                    print(rsp_title_in_quotes)
                    if not title:
                        if not isinstance(rsp_title_in_quotes, str):
                            title = llm_response_helper.convert_array_to_str(
                                rsp_title_in_quotes
                            )
                        else:
                            title = rsp_title_in_quotes
                rsp_short_summary = rsp.get("short_summary", None)
                if rsp_short_summary:
                    print(rsp_short_summary)
                    short_summary += (
                        llm_response_helper.convert_array_to_str(rsp_short_summary)
                        + "\n"
                    )
                rsp_long_summary = rsp.get("long_summary", None)
                if rsp_long_summary:
                    long_summary += (
                        llm_response_helper.convert_array_to_str(rsp_long_summary)
                        + "\n"
                    )
                rsp_paragraphs = rsp.get("paragraphs", None)
                if rsp_paragraphs:
                    paragraphs += llm_response_helper.convert_array_of_dict_to_array(
                        rsp_paragraphs
                    )

        chunk_count += 1

    short_summary = short_summary.strip()
    long_summary = long_summary.strip()
    paragraphs = [p.strip() for p in paragraphs]
    cost = _round_cost(cost)

    output_print.print_file_result(
        title=title,
        short_summary=short_summary,
        long_summary=long_summary,
        paragraphs=paragraphs,
        elapsed_seconds=elapsed_seconds,
        cost=cost,
        chunk_count=len(input_text_chunks),
        chunks_failed=chunks_failed,
    )

    if path_to_output_dir:
        output_file.write_output_file(
            title=title,
            short_summary=short_summary,
            long_summary=long_summary,
            paragraphs=paragraphs,
            elapsed_seconds=elapsed_seconds,
            cost=cost,
            path_to_input_file=path_to_input_file,
            path_to_output_dir=path_to_output_dir,
            path_to_source=path_to_input_file,
            original_path_to_input_file_or_dir_or_url=original_path_to_input_file_or_dir_or_url,
            target_language=target_language,
        )

    if path_to_move_done_files_dir:
        util_print.print_important(
            f"Moving input file {path_to_input_file} to {path_to_move_done_files_dir}"
        )
        util_file.move_file(path_to_input_file, path_to_move_done_files_dir)

    return (elapsed_seconds, cost)


def summarize_file_or_dir_or_url(
    path_to_input_file_or_dir_or_url: str,
    path_to_output_dir: str | None,
    target_language: str | None,
    path_to_move_done_files_dir: str | None,
) -> None:
    if path_to_output_dir:
        util_dir.ensure_dir_exists(path_to_output_dir)

    input_filepaths = extractor.collect_input_filepaths(
        path_to_input_file_or_dir_or_url
    )

    files_processed = 0
    files_skipped = 0
    files_bad = 0
    elapsed_seconds = 0.0
    cost = 0.0
    for path_to_input_file in input_filepaths:
        try:
            path_to_output_file = output_file.get_path_to_output_file(
                path_to_input_file, path_to_output_dir
            )
            if path_to_output_file and os.path.exists(path_to_output_file):
                util_print.print_warning(
                    f"[skipping] output file '{path_to_output_file}' already exists"
                )
                files_skipped += 1
                continue

            (_elapsed_seconds, _cost) = _summarize_one_file(
                path_to_input_file=path_to_input_file,
                target_language=target_language,
                path_to_output_dir=path_to_output_dir,
                original_path_to_input_file_or_dir_or_url=path_to_input_file_or_dir_or_url,
                path_to_move_done_files_dir=path_to_move_done_files_dir,
            )
            elapsed_seconds += _elapsed_seconds
            cost += _cost
            files_processed += 1
        except Exception as e:
            util_print.print_error(f"Exception occurred: {str(e)} [skipped file]")
            files_bad += 1

    elapsed_seconds = round(elapsed_seconds, 2)
    cost = _round_cost(cost)
    output_print.print_final_result(
        files_processed, elapsed_seconds, files_skipped, cost, files_bad
    )
