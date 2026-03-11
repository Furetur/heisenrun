#!/bin/sh
set -e

uv run ruff check
uv run mypy src/
