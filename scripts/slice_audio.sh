#!/bin/bash

# slice_audio.sh - Chunk audio files into 10-second segments with 1-second overlap
# Usage: ./slice_audio.sh input.wav [output_dir]

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <input_audio_file> [output_directory]"
    echo "Example: $0 debate.wav audio/"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_DIR="${2:-audio}"

# Validate input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Extract base filename without extension
BASENAME=$(basename "$INPUT_FILE" .wav)

echo "Slicing $INPUT_FILE into 10-second chunks with 1-second overlap..."

# Use ffmpeg to create overlapping segments
ffmpeg -i "$INPUT_FILE" -f segment -segment_time 10 -segment_overlap 1 -c copy "$OUTPUT_DIR/${BASENAME}_chunk_%03d.wav"

echo "Audio slicing complete! Chunks saved to $OUTPUT_DIR/"
