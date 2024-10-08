#!/bin/bash

# Description: This script watches for changes in a specified input file and
# triggers the processing of arXiv papers to EPUB and/or PDF format using a Python script.
# It continuously polls the input file and runs the conversion when changes are detected.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/main.py"
POLL_INTERVAL=30  # Check every 30 seconds

# Function to display usage information
show_help() {
    echo "Usage: $0 --input <input_file> --epub-output <epub_output_folder> --pdf-output <pdf_output_folder>"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message and exit"
    echo "  --input         Specify the input file to watch"
    echo "  --epub-output   Specify the output folder for converted EPUBs (optional)"
    echo "  --pdf-output    Specify the output folder for downloaded PDFs (optional)"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        --input)
            INPUT_FILE="$2"
            shift 2
            ;;
        --epub-output)
            EPUB_OUTPUT_FOLDER="$2"
            shift 2
            ;;
        --pdf-output)
            PDF_OUTPUT_FOLDER="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Check if required arguments are provided
if [ -z "$INPUT_FILE" ]; then
    echo "Error: --input argument is required"
    echo "Use -h or --help for usage information"
    exit 1
fi

# Function to handle script termination
cleanup() {
    echo
    echo "Ctrl+C caught. Exiting gracefully..."
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup SIGINT

echo "Starting arxiv-to-epub watcher..."
echo "Polling for changes to $INPUT_FILE every $POLL_INTERVAL seconds. Press Ctrl+C to exit."

last_modified=0

while true; do
    current_modified=$(stat -c %Y "$INPUT_FILE" 2>/dev/null || echo 0)
    
    if [ "$current_modified" != "$last_modified" ]; then
        echo "Change detected in $INPUT_FILE. Processing..."
        poetry run python "$PYTHON_SCRIPT" --input "$INPUT_FILE" \
            ${EPUB_OUTPUT_FOLDER:+--epub-output "$EPUB_OUTPUT_FOLDER"} \
            ${PDF_OUTPUT_FOLDER:+--pdf-output "$PDF_OUTPUT_FOLDER"}
        last_modified=$current_modified
    fi
    
    sleep $POLL_INTERVAL
done