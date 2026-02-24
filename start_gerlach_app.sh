#!/bin/bash
# Launcher script for Gerlach Personality Types App (Mac/Linux)

echo "========================================"
echo " Gerlach (2018) Personality Types App"
echo "========================================"
echo ""
echo "Starting the application..."
echo ""

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "WARNING: ANTHROPIC_API_KEY environment variable is not set!"
    echo "Please set it before running the app:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
    read -p "Press enter to continue anyway..."
fi

# Start Streamlit app
python -m streamlit run gerlach_personality_app.py --server.port 8504

