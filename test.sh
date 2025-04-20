set -e

poetry run python -m gpt_summarizer.main_cli ./data/input.txt $1 $2 $3 $4
