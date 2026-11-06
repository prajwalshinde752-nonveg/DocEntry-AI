#!/usr/bin/env bash
# Saves your API key into the .env file.
#
# Usage:
#   ./set_key.sh                  (it will ask you to paste the key)
#   ./set_key.sh AIzaSy...        (or pass the key directly)
set -e
cd "$(dirname "$0")"

key="$1"

if [ -z "$key" ]; then
  printf "Paste your API key and press Enter: "
  read -r key
fi

# Clean up common copy-paste mistakes.
key="$(printf '%s' "$key" | tr -d '[:space:]')"
key="${key#AI_API_KEY=}"          # in case the whole line was pasted
key="${key#\'}"
key="${key%\'}"
key="${key#\"}"
key="${key%\"}"

if [ -z "$key" ]; then
  echo "No key entered. Nothing changed."
  exit 1
fi

case "$key" in
  AIza*) ;;
  *) echo "Warning: Gemini keys normally start with 'AIza'. Saving anyway." ;;
esac

touch .env
if grep -q '^AI_API_KEY=' .env; then
  sed -i "s|^AI_API_KEY=.*|AI_API_KEY=${key}|" .env
else
  printf 'AI_API_KEY=%s\n' "$key" >> .env
fi

# Make sure the other settings exist.
grep -q '^AI_BASE_URL=' .env || \
  echo 'AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/' >> .env
grep -q '^AI_MODEL=' .env || \
  echo 'AI_MODEL=gemini-3.8-flash' >> .env

chmod 600 .env

echo
echo "Saved to .env (key length: ${#key})."
echo "Now open the app and press 'Test connection' in the sidebar."
