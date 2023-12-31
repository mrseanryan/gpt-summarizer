import config

def get_simple_summarize_prompt(input_text):
    return f"""
    Create a summary of this text:

    {input_text}
    """

# ref: https://www.reddit.com/r/LocalLLaMA/comments/1561vn5/here_is_a_practical_multiturn_llama2chat_prompt/?rdt=64758
# ref: https://github.com/mrseanryan/gpt-summarizer/issues/4
def get_llama_summarize_prompt(input_text):
    return f"""SYSTEM: You are a helpful text analyzer that knows how to summarize a text.
USER: Summarize this text denoted by backticks:
```{input_text}```"""
#ASSISTANT:"""

def get_chatgpt_summarize_prompt(input_text):
    return build_next_prompt(input_text, "English")

def get_chatgpt_summary_prompt_and_translate_to(input_text, target_language):
    return build_next_prompt(input_text, target_language)

OUTPUT_FORMAT = f"""
The output format must be valid JSON, with the fields: short_summary, long_summary.
"""

def build_next_prompt(input_text, target_language):
    return f"""
        Analyze the given input text, and create a short and long summary in the target language {target_language}.
        The output text must be in a formal style, intended for an advanced reader.
        
        The input text is delimited by triple backticks.

        {OUTPUT_FORMAT}

        short_summary should be {config.SHORT_SUMMARY_WORD_COUNT} words long.
        long_summary should be {config.LONG_SUMMARY_WORD_COUNT} words long.

    text: ```{input_text}```
    """
