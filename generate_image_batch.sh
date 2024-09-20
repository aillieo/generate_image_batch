#!/bin/bash

PYTHON=""
if command -v python &>/dev/null; then
    PYTHON="python"
elif command -v python3 &>/dev/null; then
    PYTHON="python3"
else
    echo "Python not available."
    exit 1
fi

$PYTHON generate_image_batch.py workflow_api.json prompts.txt
