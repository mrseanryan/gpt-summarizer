import json
import sys

import config
import prompts
import util_chat
import util_file
import util_wait

if len(sys.argv) != 2 and len(sys.argv) != 3:
    print(f"USAGE: {sys.argv[0]} <path to input text file> [target language]")
    exit(666)

path_to_input_file = sys.argv[1]
target_language = None if (len(sys.argv) < 3) else sys.argv[2]

input_text = "\n".join(util_file.read_lines_from_file(path_to_input_file))

def divide_into_chunks(list, size):
    for i in range(0, len(list), size): 
        yield list[i:i + size]

input_tokens = input_text.split(" ")
input_tokens_count = len(input_tokens)
input_text_list = []
if (input_tokens_count > config.MAIN_INPUT_TOKENS):
    print("! ! ! WARNING - Too many words in the input file! Max is {config.MAIN_INPUT_TOKENS} but that file has {input_tokens_count} words.")
    print("Splitting ...")
    chunks = divide_into_chunks(input_tokens, config.MAIN_INPUT_TOKENS)
    for chunk in chunks:
        input_text_list.append(" ".join(chunk))
else:
    input_text_list = [input_text]

if target_language is None:
    print(f"Summarizing file at '{path_to_input_file}'...")
else:
    print(f"Summarizing file at '{path_to_input_file}' into {target_language}...")

def print_separator_heading(heading):
    print(f"=== === {heading} === ===")

def dump_result(rsp):
    print_separator_heading("Short Summary")
    print(rsp['short_summary'])
    print_separator_heading("Long Summary")
    print(rsp['long_summary'])

def summarize(prompt):
    retries_remaining = config.RETRY_COUNT
    rsp_parsed = None
    while(not rsp_parsed and retries_remaining > 0):
        rsp = None
        try:
            rsp = util_chat.next_prompt(prompt)
            rsp_parsed = json.loads(rsp, strict=False)
        except Exception as error:
            try:
                # Try adding a closing } (why?)
                rsp_parsed = json.loads(rsp + "}", strict=False)
            except Exception as error:
                print("!! error: ", error)
                print("REQ: ", prompt)
                print("RSP: ", rsp)
                util_wait.wait_seconds(config.RETRY_WAIT_SECONDS)
                retries_remaining -= 1

    if rsp_parsed is None:
        print(f"!!! RETRIES EXPIRED !!!")
        exit(667)
    return rsp_parsed

for text in input_text_list:
    prompt = ""
    if target_language is None:
        prompt = prompts.get_summary_prompt_and_translate_to(input_text, target_language)
    else:
        prompt = prompts.get_summarize_prompt(input_text)
    rsp = summarize(prompt)
    dump_result(rsp)
