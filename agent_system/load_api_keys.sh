#!/bin/bash
# Shell script to export OpenRouter API keys for models
# Usage: source load_api_keys.sh

# Determine the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default to api_keys.env
SECRETS_FILE="${SCRIPT_DIR}/api_keys.env"

# Use api_keys.local.env if it exists (override)
if [ -f "${SCRIPT_DIR}/api_keys.local.env" ]; then
    SECRETS_FILE="${SCRIPT_DIR}/api_keys.local.env"
fi

if [ ! -f "$SECRETS_FILE" ]; then
    echo "ERROR: API keys file not found at $SECRETS_FILE"
    echo "Please create api_keys.local.env based on api_keys.env"
    return 1
fi

echo "Loading API keys from: $SECRETS_FILE"

# Read and export the keys
while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ "$key" =~ ^#.*$ ]] && continue
    [[ -z "$key" ]] && continue
    
    # Remove leading/trailing whitespace and quotes
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | sed 's/^["'\'']//; s/["'\'']$//' | xargs)
    
    # Export the variable
    export "$key=$value"
    echo "  Exported: $key"
done < "$SECRETS_FILE"

# Export OPENROUTER_API_KEY for xiaomi/mimo-v2-flash:free (largest model)
if [ -n "$OPENROUTER_API_KEY_XIAOMI_MIMO_V2_FLASH" ]; then
    export OPENROUTER_API_KEY="$OPENROUTER_API_KEY_XIAOMI_MIMO_V2_FLASH"
    echo ""
    echo "✓ OPENROUTER_API_KEY exported for xiaomi/mimo-v2-flash:free (largest model)"
else
    echo ""
    echo "⚠ Warning: OPENROUTER_API_KEY_XIAOMI_MIMO_V2_FLASH not found in secrets file"
fi

echo ""
echo "To use in your terminal, run: source load_api_keys.sh"
