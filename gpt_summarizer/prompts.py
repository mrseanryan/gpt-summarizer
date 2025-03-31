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
    return _build_next_complex_prompt_and_translate_to(input_text, config.TARGET_LANGUAGE)


def get_chatgpt_summarize_prompt_and_translate_to(
    input_text: str, target_language: str
) -> str:
    if config.OPEN_AI_USE_COMPLEX_PROMPT:
        return _build_next_complex_prompt_and_translate_to(input_text, target_language)
    else:
        return _build_next_simple_prompt_and_translate_to(input_text, target_language)

def get_ollama_summarize_prompt(input_text: str) -> str:
    return _build_next_simple_prompt_and_translate_to(input_text, config.TARGET_LANGUAGE)


def get_ollama_summary_prompt_and_translate_to(
    input_text: str, target_language: str
) -> str:
    return _build_next_simple_prompt_and_translate_to(input_text, target_language)


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


OUTPUT_TEXT_STYLE = "The output text preserve the original style and tone. The summary MUST summarize the contents of the text, this is NOT a commentary."

SYSTEM_PROMPT__OPENAI = f"You are a summary assistant, skilled in summarizing texts whilst preserving the main points and original style. The target language is {config.TARGET_LANGUAGE}."


def _build_next_simple_prompt_and_translate_to(input_text: str, target_language: str) -> str:
    """Simple prompt suitable for smaller LLMs, such as locally hosted LLM."""
    print("[simple prompt]")
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

def _build_next_complex_prompt_and_translate_to(input_text: str, target_language: str) -> str:
    """Complex Chain-of-thought prompt suitable for larger LLMs, such as ChatGPT."""
    print("[complex prompt]")
    return f"""Examine the provided user prompt, the text input, noting its style of writing and tone.

RULES:
R1. Do NOT mention the text, study, document or paper.
R2. Create shorted versions of the original text, in the same style.
R3. Preserve the 'person' or 'narrator' of the text: for example, if the text is written in first-person, then also output in first-person.

PROCESS TO FOLLOW:
    1. Analyze the given input text, noting its style and tone.
        - The input text is delimited by triple backticks.
    2. {_get_output_format()}
    3. Create a title and a short and long version in the target language {target_language}.
        - {OUTPUT_TEXT_STYLE}
        - short_summary should be {config.SHORT_SUMMARY_WORD_COUNT} words long, in the original style.
        - long_summary should be {config.LONG_SUMMARY_WORD_COUNT} words long, in the original style.
        - paragraphs should be an array of one sentence shortened-versions: one sentence for each paragraph.
        - shortened texts should be as if excerpts of the original text. example: 'While recent language models have the ability to take long contexts as input, relatively little is known about how well the language models
use longer context.' -> 'Whilst recent language models can accept long contexts, little is know about the quality of output'.
    4. Do NOT output a commentary - do NOT use phrases such as 'The paper examines...', 'It is noted...' or 'This text'.
    5. After generating the shortened texts, stop and check that the output is valid {get_output_format_name()}.

<thinking>
For each generated shortened text:
- check does the generated text follow the RULES.
- check is the writing style and tone same as original.
- check is the shortened text as if part of the original text NOT a commentary.
- check the shortened text is direct, as a primary source, and not a commentary.
- do NOT mention the text, study, document or paper.
- do NOT output a commentary - do NOT use phrases such as 'The paper examines...', 'It is noted...' or 'The text discusses...' or 'This text lists...' or 'The text...' or 'The study...'.
- avoid duplication
[Continue for all items]
</thinking>

text: ```{input_text}```

IMPORTANT: Only output in valid {get_output_format_name()}.

assistant: ```{get_output_format_name().lower()}
"""
