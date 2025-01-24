from . import config
import os

from cornsnake import util_dir, util_print, util_network


def _download_file(url: str) -> str:
    util_print.print_section("Downloading file")
    util_print.print_custom(f"Downloading from {url} ...")

    # add timestamp to make unique filename, since URL content may have changed
    local_filepath: str = util_network.get_file_timestamped(
        url,
        "./temp",
        prefix="downloaded-",
        text_file_extensions=config.SUPPORTED_FILE_EXTENSIONS,
    )
    util_print.print_result(f"[download complete] {local_filepath}")
    return local_filepath


def _is_url(path: str) -> bool:
    return path.startswith("http")


def collect_input_filepaths(path_to_input_file_or_dir_or_url: str) -> list[str]:
    input_filepaths = []
    if os.path.isdir(path_to_input_file_or_dir_or_url):
        for extension in config.SUPPORTED_FILE_EXTENSIONS:
            input_filepaths += util_dir.find_files_recursively(
                path_to_input_file_or_dir_or_url, extension
            )
    elif _is_url(path_to_input_file_or_dir_or_url):
        local_filepath = _download_file(path_to_input_file_or_dir_or_url)
        input_filepaths = [local_filepath]
    else:
        input_filepaths = [path_to_input_file_or_dir_or_url]
    return input_filepaths
