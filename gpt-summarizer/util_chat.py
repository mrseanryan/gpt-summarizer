import ollama
import openai

from cornsnake import util_color, util_print, util_time
from . import config
from . import prompts
from . import service_api_key
from . import util_cost_estimator
from . import util_config

local_llm = None
if util_config.is_local_via_ctransformers():
    from ctransformers import AutoModelForCausalLM

    gpu_message = (
        f"Using {config.LOCAL_CTRANSFORMERS_GPU_LAYERS} GPU layers"
        if config.IS_GPU_ENABLED
        else "NOT using GPU"
    )
    print(
        f"LOCAL AI model: {config.LOCAL_CTRANSFORMERS_MODEL_FILE_PATH} [{config.LOCAL_CTRANSFORMERS_MODEL_TYPE}] [{gpu_message}]"
    )
    local_llm = None
    if config.IS_GPU_ENABLED:
        local_llm = AutoModelForCausalLM.from_pretrained(
            config.LOCAL_CTRANSFORMERS_MODEL_FILE_PATH,
            model_type=config.LOCAL_CTRANSFORMERS_MODEL_TYPE,
            gpu_layers=config.LOCAL_CTRANSFORMERS_GPU_LAYERS,
        )
    else:
        local_llm = AutoModelForCausalLM.from_pretrained(
            config.LOCAL_CTRANSFORMERS_MODEL_FILE_PATH,
            model_type=config.LOCAL_CTRANSFORMERS_MODEL_TYPE,
        )
elif util_config.is_local_via_ollama():
    util_print.print_with_color(f"ollama model: [{config.OLLAMA_MODEL_NAME}]", util_color.bcolors.MAGENTA)
else:
    util_print.print_with_color(f"Open AI model: [{config.OPEN_AI_MODEL}]", util_color.bcolors.MAGENTA)
    openai.api_key = service_api_key.get_openai_key()


def get_completion_from_openai(prompt):
    messages = [
        {"role": "system", "content": prompts.SYSTEM_PROMPT__OPENAI},
        {"role": "user", "content": prompt},
    ]

    client = openai.OpenAI()

    response_format = None
    if util_config.is_json_not_yaml():
        response_format = { "type": "json_object" }

    response = client.chat.completions.create(
        model=config.OPEN_AI_MODEL,
        messages=messages,
        # Temperature is the degree of randomness of the model's output
        # 0 would be same each time. 0.7 or 1 would be difference each time, and less likely words can be used:
        temperature=config.TEMPERATURE,        
        response_format=response_format
    )

    estimated_cost = util_cost_estimator.estimate_openai_cost(
        response.usage.prompt_tokens, response.usage.completion_tokens
    )

    return (response.choices[0].message.content, estimated_cost)


def get_completion_from_local(prompt):
    return local_llm(prompt)


def get_completion_from_ollama(prompt):
    messages = [
        {"role": "system", "content": prompts.SYSTEM_PROMPT__OPENAI},
        {"role": "user", "content": prompt},
    ]
    response = ollama.chat(model=config.OLLAMA_MODEL_NAME, messages=messages)
    return response["message"]["content"]


def get_completion(prompt):
    if util_config.is_local_via_ctransformers():
        return (get_completion_from_local(prompt), 0.0)
    elif util_config.is_local_via_ollama():
        return (get_completion_from_ollama(prompt), 0.0)
    else:
        return get_completion_from_openai(prompt)


def send_prompt(prompt, show_input=True, show_output=True):
    if show_input:
        util_print.print_section("=== REQUEST ===")
        print(prompt)

    (response, cost) = get_completion(prompt)

    if show_output:
        util_print.print_section("=== RESPONSE ===")
        print(response)

    return (response, cost)


def next_prompt(prompt):
    start = util_time.start_timer()
    rsp = None
    if config.is_debug:
        (rsp, cost) = send_prompt(prompt)
    else:
        (rsp, cost) = send_prompt(prompt, show_input=False, show_output=False)
    elapsed_seconds = util_time.end_timer(start)
    return (rsp, elapsed_seconds, cost)
