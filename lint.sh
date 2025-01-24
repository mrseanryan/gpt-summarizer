# so future errors halt the script.
set -e

./format.sh

echo Linting ...

ruff check gpt_summarizer

python -m mypy --install-types --non-interactive gpt_summarizer

echo [done]
