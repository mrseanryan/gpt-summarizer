SHORT_SUMMARY_WORD_COUNT = 50
LONG_SUMMARY_WORD_COUNT = 300

MAIN_INPUT_WORDS = 500  # Chat-GPT has max 4097 tokens. For local model, you may want to use a lower limit for performance reasonse.
# Note: when chunking, we just split by space not by tokens.

RETRY_WAIT_SECONDS = 3
RETRY_COUNT = 3

is_debug = False

# 0 would be same each time. 0.7 or 1 would be different each time, and less likely words can be used:
TEMPERATURE = 0

OPEN_AI_MODEL = "gpt-3.5-turbo"

# To use a local LLM 'directly' via ctransformers, set this to the path to the model file.
# To use open-ai, set this to empty string ""
LOCAL_CTRANSFORMERS_MODEL_FILE_PATH = (
    ""  # "/home/sean/Downloads/models/llama-2-13b-chat.ggmlv3.q4_0.bin"
)

LOCAL_CTRANSFORMERS_MODEL_TYPE = "llama"

IS_GPU_ENABLED = False  # Requires NVidia graphics card with latest driver and version of CUDA to match ctransformers
LOCAL_CTRANSFORMERS_GPU_LAYERS = 8  # 8 worked for an NVidia card with 2 GB RAM, but maybe that also depends on the model?

TARGET_LANGUAGE = "English"

# source = https://openai.com/api/pricing/
# updated May 2024
OPENAI_COST_CURRENCY = "$"
OPENAI_COST__PER_PROMPT_ONE_MILLION_TOKENS__USD = 0.50
OPENAI_COST__PER_COMPLETION_ONE_MILLION_TOKENS__USD = 1.50

OLLAMA_MODEL_NAME = "llama3"

SUPPORTED_FILE_EXTENSIONS = [".html", ".md", ".pdf", ".txt", ".yaml"]


def _is_local_via_ctransformers():
    return len(LOCAL_CTRANSFORMERS_MODEL_FILE_PATH) > 0


def _is_local_via_ollama():
    return len(OLLAMA_MODEL_NAME) > 0


def is_local_via_ctransformers():
    is_enabled = _is_local_via_ctransformers()
    if is_enabled and _is_local_via_ollama():
        raise ValueError(
            "Please check config.py: both local via ctransformers AND ollama are enabled"
        )
    return is_enabled


def is_local_via_ollama():
    is_enabled = _is_local_via_ollama()
    if is_enabled and _is_local_via_ctransformers():
        raise ValueError(
            "Please check config.py: both local via ctransformers AND ollama are enabled"
        )
    return is_enabled
