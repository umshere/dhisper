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

# Get total duration of the input file
DURATION=$(ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$INPUT_FILE")
DURATION_INT=$(echo "$DURATION" | cut -d. -f1)

# Create overlapping segments manually
COUNTER=0
START_TIME=0

while [ $START_TIME -lt $DURATION_INT ]; do
    CHUNK_FILE=$(printf "$OUTPUT_DIR/${BASENAME}_chunk_%03d.wav" $COUNTER)
    
    echo "Creating chunk $COUNTER: ${START_TIME}s to $((START_TIME + 10))s"
    
    # Extract 10-second chunk starting at START_TIME
    ffmpeg -y -i "$INPUT_FILE" -ss $START_TIME -t 10 -c copy "$CHUNK_FILE" 2>/dev/null
    
    # Move start time forward by 9 seconds (10 - 1 second overlap)
    START_TIME=$((START_TIME + 9))
    COUNTER=$((COUNTER + 1))
done

echo "Audio slicing complete! Chunks saved to $OUTPUT_DIR/"
