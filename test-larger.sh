set -e

poetry run python -m gpt_summarizer.main_cli ./data/How-Language-Models-use-Long-Contexts.txt $1 $2 $3 $4
