# =========================
# ===   MAIN SETTINGS  ====

SHORT_SUMMARY_WORD_COUNT = 50
LONG_SUMMARY_WORD_COUNT = 300

CHUNK_SIZE_IN_WORDS = 500  # Some LLMs like Chat-GPT have a much longer context window. For a local model, you may want to use a lower limit for performance reasons.
# Note: when chunking, we just split by space not by tokens.

# 0 would be same each time. 0.7 or 1 would be different each time, and less likely words can be used:
TEMPERATURE = 0.0

SUPPORTED_FILE_EXTENSIONS = [".html", ".md", ".pdf", ".txt", ".yaml"]

TARGET_LANGUAGE = "English"

# ===========================================
# === REMOTE LLM VIA OPENAI [recommended] ===
OPEN_AI_MODEL = "gpt-4o-mini"  # gpt-3.5-turbo
#
# source = https://openai.com/api/pricing/
# updated Jan 2025
OPENAI_COST_CURRENCY = "$"
OPENAI_COST__PER_PROMPT_ONE_MILLION_TOKENS__USD = 0.15
OPENAI_COST__PER_COMPLETION_ONE_MILLION_TOKENS__USD = 0.6
OPENAI_COST__DECIMALS = 4

OPEN_AI_USE_COMPLEX_PROMPT = True  # If True, then use a more complex prompt (may be slower and slightly more expensive).

# =======================================================
# === LOCAL LLM VIA OLLAMA [recommended local option] ===
OLLAMA_MODEL_NAME = ""  # llama3 or phi3 or qwen2.5-coder:7b

# ===================================
# === LOCAL LLM VIA CTRANSFORMERS ===
#
# To use a local LLM 'directly' via ctransformers, set this to the path to the model file.
# To use open-ai, set this to empty string ""
LOCAL_CTRANSFORMERS_MODEL_FILE_PATH = (
    ""  # "/home/sean/Downloads/models/llama-2-13b-chat.ggmlv3.q4_0.bin"
)
LOCAL_CTRANSFORMERS_MODEL_TYPE = "llama"

IS_GPU_ENABLED = False  # Requires NVidia graphics card with latest driver and version of CUDA to match ctransformers.
LOCAL_CTRANSFORMERS_GPU_LAYERS = (
    8  # 8 worked for an NVidia card with 2 GB RAM, but that depends on the model.
)

# =========================
# === ADVANCED SETTINGS ===
CHUNK_OVERLAP_RATIO = (
    0.05  # When chunking, there can be split sentences. Chunk overlap mitigates this.
)
IS_DEBUG = False
IS_LOCAL__JSON_NOT_YAML = True  # YAML is generally cheaper and faster, but some LLMs may be more reliable with JSON
RETRY_COUNT = 3
RETRY_WAIT_SECONDS = 3
