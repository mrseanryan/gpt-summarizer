SHORT_SUMMARY_WORD_COUNT = 50
LONG_SUMMARY_WORD_COUNT = 300

MAIN_INPUT_TOKENS = 1500 # Chat-GPT has max 4097 tokens, but here we just split by space.

RETRY_WAIT_SECONDS = 3
RETRY_COUNT = 3

is_debug = False

# 0 would be same each time. 0.7 or 1 would be different each time, and less likely words can be used:
TEMPERATURE = 0
