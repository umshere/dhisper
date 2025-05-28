#!/bin/bash

# download_youtube.sh - Download YouTube videos for analysis
# Usage: ./download_youtube.sh "https://youtube.com/watch?v=VIDEO_ID"

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <youtube_url> [output_name]"
    echo "Example: $0 'https://youtube.com/watch?v=dQw4w9WgXcQ' debate_video"
    exit 1
fi

YOUTUBE_URL="$1"
OUTPUT_NAME="${2:-youtube_video}"
AUDIO_DIR="${3:-audio}"

# Create audio directory
mkdir -p "$AUDIO_DIR"

echo "Downloading YouTube video: $YOUTUBE_URL"

# Check if yt-dlp is installed
if ! command -v yt-dlp &> /dev/null; then
    echo "yt-dlp not found. Installing via brew..."
    brew install yt-dlp
fi

# Download video info
echo "Getting video information..."
VIDEO_TITLE=$(yt-dlp --get-title "$YOUTUBE_URL" | head -1)
VIDEO_DURATION=$(yt-dlp --get-duration "$YOUTUBE_URL" | head -1)

echo "Title: $VIDEO_TITLE"
echo "Duration: $VIDEO_DURATION"

# Download audio only in best quality
echo "Downloading audio..."
yt-dlp \
    --extract-audio \
    --audio-format wav \
    --audio-quality 0 \
    --output "$AUDIO_DIR/${OUTPUT_NAME}.%(ext)s" \
    "$YOUTUBE_URL"

# Also download video for dashboard playback
echo "Downloading video for dashboard..."
yt-dlp \
    --format "best[height<=720]" \
    --output "$AUDIO_DIR/${OUTPUT_NAME}_video.%(ext)s" \
    "$YOUTUBE_URL"

echo "Download complete!"
echo "Audio saved to: $AUDIO_DIR/${OUTPUT_NAME}.wav"
echo "Video saved to: $AUDIO_DIR/${OUTPUT_NAME}_video.*"
echo ""
echo "Next steps:"
echo "1. Process audio: ./scripts/slice_audio.sh $AUDIO_DIR/${OUTPUT_NAME}.wav"
echo "2. Run full pipeline: make process-youtube"
echo "3. Launch dashboard: streamlit run dashboard/dashboard.py"
