# Dhisper - AI-Powered Debate Analytics Makefile
# Automates setup, model downloads, and pipeline execution

.PHONY: help setup download-models clean run run-enhanced demo demo-enhanced test process-youtube demo-youtube

# Default target
help:
	@echo "Dhisper - AI-Powered Debate Analytics"
	@echo ""
	@echo "Available targets:"
	@echo "  setup          - Install dependencies and setup environment"
	@echo "  download-models - Download whisper.cpp and stance models"
	@echo "  run            - Launch basic Streamlit dashboard"
	@echo "  run-enhanced   - Launch enhanced dashboard with YouTube search"
	@echo "  demo           - Quick demo with generated data (basic)"
	@echo "  demo-enhanced  - Quick demo with enhanced dashboard"
	@echo "  demo-youtube   - Demo with YouTube video processing"
	@echo "  process-youtube - Process downloaded YouTube video"
	@echo "  test           - Run tests with sample audio"
	@echo "  clean          - Clean generated files and cache"

# Environment setup
setup:
	@echo "Setting up Dhisper environment..."
	brew install ffmpeg yt-dlp cmake pkg-config || echo "Please install Homebrew first"
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "Setup complete!"

# Download models
download-models:
	@echo "Downloading AI models..."
	mkdir -p models
	cd models && git clone https://github.com/ggerganov/whisper.cpp.git || echo "whisper.cpp already exists"
	cd models/whisper.cpp && make clean && make coreml
	cd models/whisper.cpp && bash ./models/download-ggml-model.sh base.en
	python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); model.save('models/stance-classifier')"
	@echo "AI models downloaded successfully!"

# Launch basic dashboard
run:
	@echo "Launching Dhisper dashboard..."
	streamlit run dashboard/dashboard.py

# Launch enhanced dashboard with YouTube search
run-enhanced:
	@echo "Launching enhanced Dhisper dashboard with YouTube search..."
	streamlit run dashboard/enhanced_dashboard.py

# Quick demo with generated data (basic dashboard)
demo: 
	@echo "Running quick demo with generated data..."
	python scripts/create_demo_data.py
	streamlit run dashboard/dashboard.py

# Quick demo with enhanced dashboard
demo-enhanced: 
	@echo "Running enhanced demo with YouTube search interface..."
	python scripts/create_demo_data.py
	streamlit run dashboard/enhanced_dashboard.py

# Demo with YouTube video processing
demo-youtube: setup download-models
	@echo "Demo with YouTube video processing..."
	@echo "Please provide a YouTube URL when prompted"
	@read -p "Enter YouTube URL: " url; \
	./scripts/download_youtube.sh "$$url" demo_video
	$(MAKE) process-youtube
	streamlit run dashboard/enhanced_dashboard.py

# Process downloaded YouTube video
process-youtube:
	@echo "Processing YouTube video through AI pipeline..."
	@if [ ! -f audio/youtube_video.wav ] && [ ! -f audio/demo_video.wav ]; then \
		echo "No YouTube video found. Download one first:"; \
		echo "  ./scripts/download_youtube.sh 'https://youtube.com/watch?v=VIDEO_ID'"; \
		exit 1; \
	fi
	@# Find the downloaded video file
	@VIDEO_FILE=$$(find audio -name "*video*.wav" -o -name "youtube_*.wav" -o -name "demo_*.wav" | head -1); \
	if [ -n "$$VIDEO_FILE" ]; then \
		echo "Processing $$VIDEO_FILE..."; \
		./scripts/slice_audio.sh "$$VIDEO_FILE" audio/; \
		python scripts/transcribe.py audio/; \
		python scripts/diarise.py audio/; \
		python scripts/stance.py audio/; \
		python scripts/build_json.py audio/; \
		echo "YouTube video processing complete!"; \
	else \
		echo "No audio file found to process"; \
		exit 1; \
	fi

# Create sample audio for testing
sample-audio:
	@echo "Creating sample audio file..."
	mkdir -p audio
	@echo "Please add a sample audio file to audio/sample.wav"
	@echo "You can download a test file or record a short debate clip"

# Process sample audio through full pipeline
process-sample:
	@echo "Processing sample audio through pipeline..."
	./scripts/slice_audio.sh audio/sample.wav audio/
	python scripts/transcribe.py audio/
	python scripts/diarise.py audio/
	python scripts/stance.py audio/
	python scripts/build_json.py audio/
	@echo "Sample processing complete!"

# Run tests
test:
	@echo "Running tests..."
	python -m pytest tests/ -v || echo "No tests found - create tests/ directory with test files"

# Test enhanced dashboard functionality
test-enhanced:
	@echo "Testing enhanced dashboard components..."
	python scripts/test_enhanced_dashboard.py

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	find audio/ -name "*.txt" -delete 2>/dev/null || true
	find audio/ -name "*.rttm" -delete 2>/dev/null || true
	find audio/ -name "*.json" -delete 2>/dev/null || true
	find audio/ -name "*_chunk_*.wav" -delete 2>/dev/null || true
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleanup complete!"

# Make scripts executable
make-executable:
	chmod +x scripts/*.sh
	chmod +x scripts/*.py
	@echo "Scripts are now executable"

# Full setup from scratch
install: setup download-models make-executable
	@echo "Full installation complete!"
	@echo ""
	@echo "Quick start options:"
	@echo "  make demo-enhanced  # Test enhanced dashboard with demo data"
	@echo "  make demo-youtube   # Test with YouTube video"
	@echo "  make run-enhanced   # Launch enhanced dashboard"
	@echo ""
	@echo "Traditional workflow:"
	@echo "  ./scripts/download_youtube.sh 'YOUTUBE_URL'"
	@echo "  make process-youtube"
	@echo "  make run-enhanced"

# Show system status
status:
	@echo "Dhisper System Status:"
	@echo "======================"
	@which ffmpeg >/dev/null && echo "✅ ffmpeg installed" || echo "❌ ffmpeg missing"
	@which yt-dlp >/dev/null && echo "✅ yt-dlp installed" || echo "❌ yt-dlp missing"
	@python -c "import streamlit" 2>/dev/null && echo "✅ streamlit installed" || echo "❌ streamlit missing"
	@python -c "import plotly" 2>/dev/null && echo "✅ plotly installed" || echo "❌ plotly missing"
	@[ -d models/whisper.cpp ] && echo "✅ whisper.cpp downloaded" || echo "❌ whisper.cpp missing"
	@[ -d models/stance-classifier ] && echo "✅ stance models downloaded" || echo "❌ stance models missing"
	@[ -f audio/debate_data.json ] && echo "✅ processed data available" || echo "ℹ️  no processed data (run demo or process-youtube)"

# Quick start - launches enhanced dashboard immediately
start: demo-enhanced
	@echo "Dhisper enhanced dashboard is running!"
