import config

ONE_MILLION = 1000000


def _cost(tokens, cost_per_million):
    return (tokens * cost_per_million) / ONE_MILLION


def estimate_openai_cost(prompt_tokens, completion_tokens):
    return _cost(
        prompt_tokens, config.OPENAI_COST__PER_PROMPT_ONE_MILLION_TOKENS__USD
    ) + _cost(
        completion_tokens, config.OPENAI_COST__PER_COMPLETION_ONE_MILLION_TOKENS__USD
    )
