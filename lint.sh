# so future errors halt the script.
set -e

./format.sh

echo Linting ...

poetry run python -m ruff check gpt_summarizer

poetry run python -m mypy --install-types --non-interactive gpt_summarizer

echo [done]
