import json5
from typing import Any, Tuple
import yaml

from cornsnake import util_print, util_wait

from . import config
from . import llm_response_helper
from . import util_chat
from . import util_config

RSP_AND_METADATA = Tuple[
    dict[str, Any] | None, float, float
]  # (rsp_parsed, elapsed_seconds, total_cost)


def send_to_llm_with_retry(prompt: str) -> RSP_AND_METADATA:
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
            rsp = llm_response_helper.clean_response(rsp)
            rsp_parsed = None
            if util_config.is_json_not_yaml():
                rsp_parsed = json5.loads(rsp)  # a bit more robust than json package
            else:
                rsp_parsed = yaml.safe_load(rsp)
        except Exception as error:
            util_print.print_error("Error parsing response")
            util_print.print_error(error)
            if config.IS_DEBUG:
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
