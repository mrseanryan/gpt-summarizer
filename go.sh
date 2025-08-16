#!/bin/bash
set -e
poetry run python -m gpt_summarizer.main_cli "$@"
