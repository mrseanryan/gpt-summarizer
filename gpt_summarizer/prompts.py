from . import config
from . import util_config


def get_simple_summarize_prompt(input_text: str) -> str:
    return f"""
    Create a summary of this text:

    {input_text}
    """


# ref: https://www.reddit.com/r/LocalLLaMA/comments/1561vn5/here_is_a_practical_multiturn_llama2chat_prompt/?rdt=64758
# ref: https://github.com/mrseanryan/gpt-summarizer/issues/4
def get_llama_summarize_prompt(input_text: str) -> str:
    return f"""SYSTEM: You are a helpful text analyzer that knows how to summarize a text into valid {get_output_format_name()}.
USER: Summarize this text denoted by backticks:
```{input_text}```"""


def get_chatgpt_summarize_prompt(input_text: str) -> str:
    return build_next_prompt(input_text, config.TARGET_LANGUAGE)


def get_chatgpt_summary_prompt_and_translate_to(
    input_text: str, target_language: str
) -> str:
    return build_next_prompt(input_text, target_language)


def get_ollama_summarize_prompt(input_text: str) -> str:
    return get_chatgpt_summarize_prompt(input_text)


def get_ollama_summary_prompt_and_translate_to(
    input_text: str, target_language: str
) -> str:
    return get_chatgpt_summary_prompt_and_translate_to(input_text, target_language)


# yaml is cheaper to generate
OUTPUT_FORMAT_YAML = """
The output format must be valid YAML, with the fields: title_in_quotes, short_summary, long_summary, paragraphs.
- do NOT include YAML special characters in the text (for example: single quotes or colons)
- do NOT use the line-continuation operator '|'
- for bullets use hyphen '-', do NOT use '*'
- denote the overall output with ``` NOT '---'
"""

OUTPUT_FORMAT_JSON = """
The output format must be valid JSON, with the fields: title_in_quotes, short_summary, long_summary, paragraphs.
"""


def _get_output_format() -> str:
    if util_config.is_json_not_yaml():
        return OUTPUT_FORMAT_JSON
    return OUTPUT_FORMAT_YAML


def get_output_format_name() -> str:
    if util_config.is_json_not_yaml():
        return "JSON"
    return "YAML"


OUTPUT_TEXT_STYLE = "The output text must use a formal style, intended for an advanced reader. The summary should summarize the contents of the text, not comment on it."

SYSTEM_PROMPT__OPENAI = f"You are a summary assistant, skilled in summarizing texts whilst preserving the main points. The target language is {config.TARGET_LANGUAGE}."


def build_next_prompt(input_text: str, target_language: str) -> str:
    return f"""
        1. Analyze the given input text.
          - The input text is delimited by triple backticks.
        2. {_get_output_format()}
        3. Create a title and a short and long summary in the target language {target_language}.
          - {OUTPUT_TEXT_STYLE}
          - short_summary should be {config.SHORT_SUMMARY_WORD_COUNT} words long.
          - long_summary should be {config.LONG_SUMMARY_WORD_COUNT} words long.
          - paragraphs should be an array of one sentence summaries: one sentence for each paragraph.
        4. After generating the summaries, stop and check that the output is valid {get_output_format_name()}.

    text: ```{input_text}```

    IMPORTANT: Only output in valid {get_output_format_name()}.

    assistant: ```{get_output_format_name().lower()}
    """
