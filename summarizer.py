import json
import os
import html2text
import yaml
from datetime import datetime

from cornsnake import (
    util_print,
    util_file,
    util_time,
    util_wait,
    util_dir,
    util_network,
)

import config
import prompts
import util_chat


def _clean_response(text):
    prelim_with_yaml = "```yaml"  # yaml is cheaper to generate
    if prelim_with_yaml in text:
        text = text.split(prelim_with_yaml)[1]
    end = "```"
    if end in text:
        text = text.split(end)[0]
    return text


def _summarize_via_open_ai(prompt):
    retries_remaining = config.RETRY_COUNT
    rsp_parsed = None
    elapsed_seconds = 0
    total_cost = 0.0
    while not rsp_parsed and retries_remaining > 0:
        rsp = None
        try:
            (rsp, _elapsed_seconds, cost) = util_chat.next_prompt(prompt)
            elapsed_seconds += _elapsed_seconds
            total_cost += cost
            rsp = _clean_response(rsp)
            rsp_parsed = yaml.safe_load(rsp)
        except Exception as error:
            print("!! error: ", error)
            if config.is_debug:
                print("REQ: ", prompt)
                print("RSP: ", rsp)
            util_wait.wait_seconds(config.RETRY_WAIT_SECONDS)
            retries_remaining -= 1

    if rsp_parsed is None:
        print(f"!!! RETRIES EXPIRED !!!")
    return (rsp_parsed, elapsed_seconds, total_cost)


def _summarize_via_local(prompt):
    return util_chat.next_prompt(prompt)


def _divide_into_chunks(list, size):
    for i in range(0, len(list), size):
        yield list[i : i + size]


def _get_path_to_output_file(path_to_input_file, path_to_output_dir):
    if not path_to_output_dir:
        return None
    input_filename = util_file.get_last_part_of_path(path_to_input_file)
    output_filename = util_file.change_extension(
        input_filename, ".yaml.txt"
    )  # adding .txt so can preview in Windows Explorer, Dropbox etc.
    path_to_output_file = os.path.join(path_to_output_dir, output_filename)
    return path_to_output_file


def _write_output_file(
    short_summary, long_summary, paragraphs, elapsed_seconds, cost, path_to_output_file
):
    file_result = {}
    file_result["short_summary"] = short_summary
    file_result["long_summary"] = long_summary
    file_result["paragraphs"] = paragraphs
    file_result["total_time_seconds"] = elapsed_seconds
    file_result["total_estimated_cost_currency"] = config.OPENAI_COST_CURRENCY
    file_result["total_estimated_cost"] = cost
    yaml_text = yaml.dump(file_result)
    util_print.print_important(f"Writing YAML file to {path_to_output_file}")
    util_file.write_text_to_file(yaml_text, path_to_output_file)


def _chunk_text_by_words(input_text):
    input_words = input_text.split(" ")
    input_tokens_count = len(input_words)
    input_text_list = []

    if input_tokens_count > config.MAIN_INPUT_WORDS:
        util_print.print_warning(
            f"The input file has many words! Max is {config.MAIN_INPUT_WORDS} but that file has {input_tokens_count} words."
        )
        chunks = _divide_into_chunks(input_words, config.MAIN_INPUT_WORDS)
        input_text_list = []
        for chunk in chunks:
            input_text_list.append(" ".join(chunk))
        print(f"Split into {len(input_text_list)} chunks")
    else:
        input_text_list = [input_text]
    return input_text_list


def _print_file_result(short_summary, long_summary, paragraphs, elapsed_seconds, cost):
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


def _extract_text(path_to_input_file):
    input_text = util_file.read_text_from_text_or_pdf_file_skipping_comments(
        path_to_input_file
    )
    if path_to_input_file.endswith(".html"):
        return html2text.html2text(input_text)

    return input_text


def _convert_array_to_str(a):
    """
    Occasionally LLM can return a dict where str was expected
    """
    if isinstance(a, str):
        return a
    if isinstance(a, dict):
        util_print.print_warning("Unexpected response format: Converting dict to str")
        return yaml.dump(a)
    return a


def _summarize_one_file(path_to_input_file, target_language, path_to_output_dir):
    input_text = _extract_text(path_to_input_file)

    input_text_chunks = _chunk_text_by_words(input_text)

    util_print.print_section(f"Summarizing '{path_to_input_file}'")

    if target_language is None:
        print(f"Summarizing file at '{path_to_input_file}'...")
    else:
        print(f"Summarizing file at '{path_to_input_file}' into {target_language}...")

    short_summary = ""
    long_summary = ""
    paragraphs = []
    elapsed_seconds = 0
    cost = 0.0

    chunk_count = 1
    for text in input_text_chunks:
        prompt = ""
        if config.is_local():
            # TODO try fix
            if target_language is not None:
                raise (f"target_language is only supported when using Open AI ChatGPT")
            prompt = prompts.get_simple_summarize_prompt(text)
            if config.LOCAL_MODEL_TYPE == "llama":
                prompt = prompts.get_llama_summarize_prompt(text)
            (response_plain, _elapsed_seconds) = _summarize_via_local(prompt)
            elapsed_seconds += _elapsed_seconds
            rsp = {"short_summary": response_plain}
        else:
            if target_language is None:
                prompt = prompts.get_chatgpt_summarize_prompt(text)
            else:
                prompt = prompts.get_chatgpt_summary_prompt_and_translate_to(
                    text, target_language
                )
            (rsp, _elapsed_seconds, _cost) = _summarize_via_open_ai(prompt)
            elapsed_seconds += _elapsed_seconds
            cost += _cost

        util_print.print_section(
            f"Short Summary = Chunk {chunk_count} of {len(input_text_chunks)}"
        )
        if rsp is not None:
            if "short_summary" in rsp:
                print(rsp["short_summary"])
                short_summary += _convert_array_to_str(rsp["short_summary"]) + "\n"
            if "long_summary" in rsp:
                long_summary += _convert_array_to_str(rsp["long_summary"]) + "\n"
            if "paragraphs" in rsp:
                paragraphs += _convert_array_to_str(rsp["paragraphs"])

        chunk_count += 1

    _print_file_result(short_summary, long_summary, paragraphs, elapsed_seconds, cost)

    path_to_output_file = _get_path_to_output_file(
        path_to_input_file, path_to_output_dir
    )

    if path_to_output_file:
        _write_output_file(
            short_summary,
            long_summary,
            paragraphs,
            elapsed_seconds,
            cost,
            path_to_output_file,
        )

    return (elapsed_seconds, cost)


def _print_final_result(files_processed, elapsed_seconds, files_skipped, cost):
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


def _get_file_name_from_url(url):
    # credit to scottleibrand

    # Strip any trailing /'s from the end of the URL
    stripped_url = url.rstrip("/")

    # Get the base name of the URL
    base_name = stripped_url.split("/")[-1]

    for ext in config.SUPPORTED_FILE_EXTENSIONS:
        if base_name.endswith(ext):
            return base_name

    return base_name + ".html"


def _download_file(url):
    filename = _get_file_name_from_url(url)

    # add timestamp to make unique filename, since URL content may have changed
    now = datetime.now()
    timestamp = now.strftime("%Y_%m_%d__%H%M%S")
    filename_parts = filename.split(".")
    extension = filename_parts[-1]
    filename_parts = filename_parts[:-1]
    filename_parts += [timestamp, extension]
    new_filename = ".".join(filename_parts)

    local_filepath = os.path.join("./temp", f"downloaded-{new_filename}")

    util_print.print_section(f"Downloading file")
    util_print.print_custom(f"Downloading from {url} to {local_filepath} ...")
    util_network.get_file(url, local_filepath)
    util_print.print_result("[download complete]")
    return local_filepath


def _is_url(path):
    return path.startswith("http")


def summarize_file_or_dir_or_url(
    path_to_input_file_or_dir_or_url, path_to_output_dir, target_language
):
    if path_to_output_dir:
        util_dir.ensure_dir_exists(path_to_output_dir)

    input_filepaths = []
    if os.path.isdir(path_to_input_file_or_dir_or_url):
        for extension in config.SUPPORTED_FILE_EXTENSIONS:
            input_filepaths += util_dir.find_files_recursively(
                path_to_input_file_or_dir_or_url, extension
            )
    if _is_url(path_to_input_file_or_dir_or_url):
        local_filepath = _download_file(path_to_input_file_or_dir_or_url)
        input_filepaths = [local_filepath]
    else:
        input_filepaths = [path_to_input_file_or_dir_or_url]

    files_processed = 0
    files_skipped = 0
    elapsed_seconds = 0
    cost = 0
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
            path_to_input_file, target_language, path_to_output_dir
        )
        elapsed_seconds += _elapsed_seconds
        cost += _cost
        files_processed += 1

    _print_final_result(files_processed, elapsed_seconds, files_skipped, cost)