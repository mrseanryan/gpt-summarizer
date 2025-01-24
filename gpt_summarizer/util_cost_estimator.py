from . import config

ONE_MILLION = 1000000


def _cost(tokens: int, cost_per_million: float) -> float:
    return (tokens * cost_per_million) / ONE_MILLION


# TODO (someone): Look at LiteLlm https://docs.litellm.ai/docs/completion/token_usage
def estimate_openai_cost(prompt_tokens: int, completion_tokens: int) -> float:
    return _cost(
        prompt_tokens, config.OPENAI_COST__PER_PROMPT_ONE_MILLION_TOKENS__USD
    ) + _cost(
        completion_tokens, config.OPENAI_COST__PER_COMPLETION_ONE_MILLION_TOKENS__USD
    )
