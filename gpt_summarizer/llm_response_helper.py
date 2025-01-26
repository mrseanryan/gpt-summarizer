import yaml
from cornsnake import util_print

from . import prompts


def clean_response(text: str | None) -> str:
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


def convert_array_to_str(a: str | dict | list) -> str:
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


def convert_array_of_dict_to_array(a_list: str | dict | list) -> list[str]:
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
