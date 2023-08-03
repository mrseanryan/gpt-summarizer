import config

def get_simple_summarize_prompt(input_text):
    return f"""
    Create a summary of this text:

    {input_text}
    """

def get_summarize_prompt(input_text):
    return build_next_prompt(input_text, "English")

def get_summary_prompt_and_translate_to(input_text, target_language):
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
