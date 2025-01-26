import datetime
import os
import yaml
from collections import OrderedDict
from cornsnake import (
    util_print,
    util_file,
)
from typing import Any

from . import config
from . import util_config
from . import util_version


def get_path_to_output_file(
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


def write_output_file(
    title: str,
    short_summary: str,
    long_summary: str,
    paragraphs: list[str],
    elapsed_seconds: float,
    cost: float,
    path_to_input_file: str,
    path_to_output_dir: str,
    path_to_source: str,
    original_path_to_input_file_or_dir_or_url: str,
    target_language: str | None,
) -> None:
    path_to_output_file = get_path_to_output_file(
        path_to_input_file=path_to_input_file, path_to_output_dir=path_to_output_dir
    )

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
