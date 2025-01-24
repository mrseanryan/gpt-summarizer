import datetime
import os
from typing import Any, Generator, Tuple
import html2text
import json5
import yaml
from collections import OrderedDict

from cornsnake import (
    util_print,
    util_file,
    util_time,
    util_wait,
    util_dir,
)

from . import config
from . import extractor
from . import prompts
from . import util_chat
from . import util_config
from . import util_version


def _clean_response(text: str | None) -> str:
    if not text:
        return ""

    prelim_with_data_format = f"```{prompts.get_output_format_name().lower()}"
    if prelim_with_data_format in text:
        text = text.split(prelim_with_data_format)[1]

    delimit = "```"
    if delimit in text:
        parts = text.split(delimit)
        max_len = 0
        selected = ""
        for part in parts:
            if len(part) > max_len:
                selected = part
                max_len = len(part)
        return selected
    return text


RSP_AND_METADATA = Tuple[
    dict[str, Any] | None, float, float
]  # (rsp_parsed, elapsed_seconds, total_cost)


def _summarize_with_retry(prompt: str) -> RSP_AND_METADATA:
    retries_remaining = config.RETRY_COUNT
    rsp_parsed = None
    elapsed_seconds = 0.0
    total_cost = 0.0
    while not rsp_parsed and retries_remaining > 0:
        rsp = None
        try:
            (rsp, _elapsed_seconds, cost) = util_chat.next_prompt(prompt)
            elapsed_seconds += _elapsed_seconds
            total_cost += cost
            rsp = _clean_response(rsp)
            rsp_parsed = None
            if util_config.is_json_not_yaml():
                rsp_parsed = json5.loads(rsp)  # a bit more robust than json package
            else:
                rsp_parsed = yaml.safe_load(rsp)
        except Exception as error:
            util_print.print_error("Error parsing response")
            util_print.print_error(error)
            if config.is_debug:
                print("REQ: ", prompt)
                print("RSP: ", rsp)
            if util_config.is_openai():
                util_wait.wait_seconds(config.RETRY_WAIT_SECONDS)
            retries_remaining -= 1
            if retries_remaining:
                util_print.print_warning("Retrying...")

    if rsp_parsed is None:
        util_print.print_error("!!! RETRIES EXPIRED !!!")
    return (rsp_parsed, elapsed_seconds, total_cost)


def _divide_into_chunks(list: list[str], size: int) -> Generator[list[str], None, None]:
    for i in range(0, len(list), size):
        yield list[i : i + size]


def _get_path_to_output_file(
    path_to_input_file: str, path_to_output_dir: str | None
) -> str | None:
    if not path_to_output_dir:
        return None
    input_filename = util_file.get_last_part_of_path(path_to_input_file)
    output_filename = util_file.change_extension(
        input_filename, ".yaml.txt"
    )  # adding .txt so can preview in Windows Explorer, Dropbox etc.
    path_to_output_file = os.path.join(path_to_output_dir, output_filename)
    return path_to_output_file


def _write_output_file(
    title: str,
    short_summary: str,
    long_summary: str,
    paragraphs: list[str],
    elapsed_seconds: float,
    cost: float,
    path_to_output_file: str,
    path_to_source: str,
    original_path_to_input_file_or_dir_or_url: str,
    target_language: str | None,
) -> None:
    file_result = OrderedDict[str, str | list[str] | OrderedDict[str, Any]]()
    file_result["title"] = title
    file_result["short_summary"] = short_summary
    file_result["long_summary"] = long_summary
    file_result["paragraphs"] = paragraphs

    run_info = OrderedDict(
        {
            "total_time_seconds": elapsed_seconds,
            "total_estimated_cost_currency": config.OPENAI_COST_CURRENCY,
            "total_estimated_cost": cost,
        }
    )
    file_result["run_info"] = run_info

    tool_info = OrderedDict(
        {
            "tool_name": "gpt-summarizer",
            "tool_version": util_version.VERSION,
            "llm": util_config.get_llm_model(),
            "platform": util_config.get_platform(),
        }
    )
    file_result["tool_info"] = tool_info

    file_result["summary_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_result["source_path"] = path_to_source
    file_result["original_source_path"] = original_path_to_input_file_or_dir_or_url
    if target_language:
        file_result["target_language"] = target_language

    yaml.add_representer(
        OrderedDict,
        lambda dumper, data: dumper.represent_mapping(
            "tag:yaml.org,2002:map", data.items()
        ),
    )
    yaml_text = yaml.dump(file_result)
    util_print.print_important(f"Writing YAML file to {path_to_output_file}")
    util_file.write_text_to_file(yaml_text, path_to_output_file)


def _chunk_text_by_words(input_text: str) -> list[str]:
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


def _print_file_result(
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

    util_print.print_section("FULL paragraphs Summary")
    print("\n".join(paragraphs))

    util_print.print_result(
        f" -- THIS FILE time: {util_time.describe_elapsed_seconds(elapsed_seconds)}"
    )
    if cost > 0:
        util_print.print_important(
            f" -- THIS FILE estimated cost: {config.OPENAI_COST_CURRENCY}{cost}"
        )
    if chunks_failed > 0:
        util_print.print_warning(
            f"{chunks_failed} of {chunk_count} document chunks were skipped. If the summary is not of high quality, you can re-run with smaller chunks, by reducing MAIN_INPUT_WORDS in config.py."
        )


def _extract_text(path_to_input_file: str) -> str:
    input_text: str = util_file.read_text_from_text_or_pdf_file_skipping_comments(
        path_to_input_file
    )
    if path_to_input_file.endswith(".html"):
        return html2text.html2text(input_text)

    return input_text


def _convert_array_to_str(a: str | dict | list) -> str:
    """
    Occasionally LLM can return a dict where str was expected
    """
    if isinstance(a, str):
        return a
    if isinstance(a, dict):
        util_print.print_warning("Unexpected response format: Converting dict to str")
        return yaml.dump(a)
    if isinstance(a, list):
        util_print.print_warning("Unexpected response format: Converting list to str")
        return yaml.dump(a)
    return a


def _convert_array_of_dict_to_array(a_list: str | dict | list) -> list[str]:
    if isinstance(a_list, list):
        new_list = []
        for a1 in a_list:
            if isinstance(a1, dict):
                new_list.append(yaml.dump(a1))
            elif isinstance(a1, list):
                new_list += a1
            else:
                new_list.append(a1)
        return new_list
    elif isinstance(a_list, dict):
        return [yaml.dump(a_list)]
    elif isinstance(a_list, str):
        return [a_list]
    return a_list


def _summarize_one_file(
    path_to_input_file: str,
    target_language: str | None,
    path_to_output_dir: str | None,
    original_path_to_input_file_or_dir_or_url: str,
) -> Tuple[float, float]:  # (elapsed_seconds, cost)
    util_print.print_section(f"Summarizing '{path_to_input_file}'")

    input_text = _extract_text(path_to_input_file)
    input_text_chunks = _chunk_text_by_words(input_text)

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
            (response_plain, _elapsed_seconds, _cost) = _summarize_with_retry(prompt)
            elapsed_seconds += _elapsed_seconds
            rsp = {"short_summary": response_plain}
        elif util_config.is_local_via_ollama():
            if target_language is None:
                prompt = prompts.get_ollama_summarize_prompt(text)
            else:
                prompt = prompts.get_ollama_summary_prompt_and_translate_to(
                    text, target_language
                )
            (rsp, _elapsed_seconds, _cost) = _summarize_with_retry(prompt)
            elapsed_seconds += _elapsed_seconds
            cost += _cost
        elif util_config.is_openai():
            if target_language is None:
                prompt = prompts.get_chatgpt_summarize_prompt(text)
            else:
                prompt = prompts.get_chatgpt_summary_prompt_and_translate_to(
                    text, target_language
                )
            (rsp, _elapsed_seconds, _cost) = _summarize_with_retry(prompt)
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
                            title = _convert_array_to_str(rsp_title_in_quotes)
                        else:
                            title = rsp_title_in_quotes
                rsp_short_summary = rsp.get("short_summary", None)
                if rsp_short_summary:
                    print(rsp_short_summary)
                    short_summary += _convert_array_to_str(rsp_short_summary) + "\n"
                rsp_long_summary = rsp.get("long_summary", None)
                if rsp_long_summary:
                    long_summary += _convert_array_to_str(rsp_long_summary) + "\n"
                rsp_paragraphs = rsp.get("paragraphs", None)
                if rsp_paragraphs:
                    paragraphs += _convert_array_of_dict_to_array(rsp_paragraphs)

        chunk_count += 1

    short_summary = short_summary.strip()
    long_summary = long_summary.strip()
    paragraphs = [p.strip() for p in paragraphs]

    _print_file_result(
        title,
        short_summary,
        long_summary,
        paragraphs,
        elapsed_seconds,
        cost,
        len(input_text_chunks),
        chunks_failed,
    )

    path_to_output_file = _get_path_to_output_file(
        path_to_input_file=path_to_input_file, path_to_output_dir=path_to_output_dir
    )

    if path_to_output_file:
        _write_output_file(
            title=title,
            short_summary=short_summary,
            long_summary=long_summary,
            paragraphs=paragraphs,
            elapsed_seconds=elapsed_seconds,
            cost=cost,
            path_to_output_file=path_to_output_file,
            path_to_source=path_to_input_file,
            original_path_to_input_file_or_dir_or_url=original_path_to_input_file_or_dir_or_url,
            target_language=target_language,
        )

    return (elapsed_seconds, cost)


def _print_final_result(
    files_processed: int, elapsed_seconds: float, files_skipped: int, cost: float
) -> None:
    util_print.print_section("Completed")
    util_print.print_result(
        f"{files_processed} files processed in {util_time.describe_elapsed_seconds(elapsed_seconds)}"
    )
    if files_skipped > 0:
        util_print.print_result(f"{files_skipped} files skipped")
    if cost > 0:
        util_print.print_important(
            f" -- Total estimated cost: {config.OPENAI_COST_CURRENCY}{cost}"
        )


def summarize_file_or_dir_or_url(
    path_to_input_file_or_dir_or_url: str,
    path_to_output_dir: str | None,
    target_language: str | None,
) -> None:
    if path_to_output_dir:
        util_dir.ensure_dir_exists(path_to_output_dir)

    input_filepaths = extractor.collect_input_filepaths(
        path_to_input_file_or_dir_or_url
    )

    files_processed = 0
    files_skipped = 0
    elapsed_seconds = 0.0
    cost = 0.0
    for path_to_input_file in input_filepaths:
        path_to_output_file = _get_path_to_output_file(
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
        )
        elapsed_seconds += _elapsed_seconds
        cost += _cost
        files_processed += 1

    elapsed_seconds = round(elapsed_seconds, 2)
    _print_final_result(files_processed, elapsed_seconds, files_skipped, cost)
