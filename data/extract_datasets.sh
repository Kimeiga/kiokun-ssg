#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Define directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATASETS_DIR="$SCRIPT_DIR/datasets"
EXTRACTED_DIR="$DATASETS_DIR/extracted"

# Ensure the extracted directory exists
mkdir -p "$EXTRACTED_DIR"

# Function to extract .xz files
extract_xz() {
    for file in "$DATASETS_DIR"/*.xz; do
        if [ -f "$file" ]; then
            echo "Extracting $file..."
            xz -dc "$file" > "$EXTRACTED_DIR/$(basename "${file%.xz}")"
        fi
    done
}

# Extract all .xz files
echo "Extracting compressed files..."
extract_xz
