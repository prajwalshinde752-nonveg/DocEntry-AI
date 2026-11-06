#!/usr/bin/env bash
# Start DocEntry-AI
set -e
cd "$(dirname "$0")"
exec .venv/bin/streamlit run app.py
