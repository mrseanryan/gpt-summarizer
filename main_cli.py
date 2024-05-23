import json
import sys

from cornsnake import util_print

import config
import prompts
import util_chat
import util_file
import util_time
import util_wait

if len(sys.argv) != 2 and len(sys.argv) != 3:
    print(f"USAGE: {sys.argv[0]} <path to input text file> [target language]")
    exit(666)

path_to_input_file = sys.argv[1]
target_language = None if (len(sys.argv) < 3) else sys.argv[2]

input_text = util_file.read_text_from_file(path_to_input_file)

def divide_into_chunks(list, size):
    for i in range(0, len(list), size): 
        yield list[i:i + size]

input_tokens = input_text.split(" ")
input_tokens_count = len(input_tokens)
input_text_list = []

if (input_tokens_count > config.MAIN_INPUT_WORDS):
    print(f"! ! ! WARNING - Too many words in the input file! Max is {config.MAIN_INPUT_WORDS} but that file has {input_tokens_count} words.")
    chunks = divide_into_chunks(input_tokens, config.MAIN_INPUT_WORDS)
    input_text_list = []
    for chunk in chunks:
        input_text_list.append(" ".join(chunk))
    print(f"Split into {len(input_text_list)} chunks")
else:
    input_text_list = [input_text]

if target_language is None:
    print(f"Summarizing file at '{path_to_input_file}'...")
else:
    print(f"Summarizing file at '{path_to_input_file}' into {target_language}...")

def print_separator_heading(heading):
    util_print.print_section(heading)

def _clean_response(text):
    prelim_with_json = "```json"
    if prelim_with_json in text:
        text = text.split(prelim_with_json)[1]
    end = "```"
    if end in text:
        text = text.split(end)[0]
    return text

def summarize_via_open_ai(prompt):
    retries_remaining = config.RETRY_COUNT
    rsp_parsed = None
    elapsed_seconds = 0
    total_cost = 0.0
    while(not rsp_parsed and retries_remaining > 0):
        rsp = None
        try:
            (rsp, _elapsed_seconds, cost) = util_chat.next_prompt(prompt)
            elapsed_seconds += _elapsed_seconds
            total_cost += cost
            rsp = _clean_response(rsp)
            rsp_parsed = json.loads(rsp, strict=False)  # TODO consider using json5 which is more forgiving
        except Exception as error:
            print("!! error: ", error)
            if rsp is not None:
                try:
                    # Try adding a closing } (why can't AI just make valid JSON ... ?)
                    rsp_parsed = json.loads(rsp + "}", strict=False)
                except Exception as error:
                    print("!! error: ", error)
                    # Just treat the response as text, not JSON:
                    rsp_parsed={
                        'short_summary': rsp,
                        'long_summary': rsp
                    }
            else:
                if config.is_debug:
                    print("REQ: ", prompt)
                    print("RSP: ", rsp)
                util_wait.wait_seconds(config.RETRY_WAIT_SECONDS)
                retries_remaining -= 1

    if rsp_parsed is None:
        print(f"!!! RETRIES EXPIRED !!!")
    return (rsp_parsed, elapsed_seconds, total_cost)

def summarize_via_local(prompt):
    return util_chat.next_prompt(prompt)

short_summary = ""
long_summary = ""
paragraphs = []
elapsed_seconds = 0
cost = 0.0

chunk_count = 1
for text in input_text_list:
    prompt = ""
    if config.is_local():
        # TODO try fix
        if target_language is not None:
            raise(f"target_language is only supported when using Open AI ChatGPT")
        prompt = prompts.get_simple_summarize_prompt(text)
        if config.LOCAL_MODEL_TYPE == "llama":
            prompt = prompts.get_llama_summarize_prompt(text)
        (response_plain, _elapsed_seconds) = summarize_via_local(prompt)
        elapsed_seconds += _elapsed_seconds
        rsp = {
            'short_summary': response_plain
        }
    else:
        if target_language is None:
            prompt = prompts.get_chatgpt_summarize_prompt(text)
        else:
            prompt = prompts.get_chatgpt_summary_prompt_and_translate_to(text, target_language)
        (rsp, _elapsed_seconds, _cost) = summarize_via_open_ai(prompt)
        elapsed_seconds += _elapsed_seconds
        cost += _cost

    print_separator_heading(f"Short Summary = Chunk {chunk_count} of {len(input_text_list)}")
    if rsp is not None:
        if 'short_summary' in rsp:
            print(rsp['short_summary'])
            short_summary += rsp['short_summary'] + "\n"
        if 'long_summary' in rsp:
            long_summary += rsp['long_summary'] + "\n"
        if 'paragraphs' in rsp:
            paragraphs += rsp['paragraphs']

    chunk_count += 1

print_separator_heading("FULL Short Summary")
print(short_summary)

print_separator_heading("FULL Long Summary")
print(long_summary)

print_separator_heading("FULL paragraphs Summary")
print("\n".join(paragraphs))

util_print.print_result(f" -- Total time: {util_time.describe_elapsed_seconds(elapsed_seconds)}")
if cost > 0:
    util_print.print_important(f" -- Total estimated cost: {config.OPENAI_COST_CURRENCY}{cost}")
