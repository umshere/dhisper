# Testing Dhisper - Quick Start Guide

## 🚀 Immediate Testing (5 minutes)

### Option 1: Full Setup Test

```bash
# 1. Install dependencies
make setup

# 2. Download models (takes ~10 minutes)
make download-models

# 3. Add sample audio file to audio/sample.wav
# (Download any debate clip or political speech)

# 4. Run full pipeline
make demo
```

### Option 2: Quick Demo Test (No Models Required)

```bash
# 1. Install only basic dependencies
pip install streamlit plotly pandas numpy

# 2. Create mock data for testing
python scripts/create_demo_data.py

# 3. Launch dashboard with demo data
streamlit run dashboard/dashboard.py
```

## 📁 Sample Audio Sources

### Free Debate Audio

- **C-SPAN**: https://www.c-span.org/ (download any debate clip)
- **YouTube**: Use `yt-dlp` to download political debates
- **Presidential Debates**: Commission on Presidential Debates archive

### Quick Test Commands

```bash
# Download sample with yt-dlp (if installed)
yt-dlp -x --audio-format wav "https://youtube.com/watch?v=DEBATE_ID" -o "audio/sample.%(ext)s"

# Or use any audio file you have
cp ~/Downloads/your_audio.mp3 audio/
ffmpeg -i audio/your_audio.mp3 audio/sample.wav
```

## 🧪 Testing Without Audio

If you don't have audio files, test the dashboard with generated data:

```bash
# Create demo data
python scripts/create_demo_data.py

# Launch dashboard
streamlit run dashboard/dashboard.py
```

## ⚡ Fastest Test (30 seconds)

```bash
# 1. Install minimal dependencies
pip install streamlit plotly pandas numpy

# 2. Create and run demo
python scripts/create_demo_data.py && streamlit run dashboard/dashboard.py
```

## 🔧 Troubleshooting

### Common Issues

1. **Missing ffmpeg**: `brew install ffmpeg`
2. **Python version**: Requires Python 3.9+
3. **Missing models**: Run `make download-models`
4. **HuggingFace token**: Required for pyannote.audio diarization

### Skip Model Downloads for Quick Test

```bash
# Test only transcription (no diarization/stance)
./scripts/slice_audio.sh audio/sample.wav
# Skip: python scripts/transcribe.py audio/  (needs whisper model)
# Skip: python scripts/diarise.py audio/     (needs HF token)
# Skip: python scripts/stance.py audio/      (needs sentence transformers)
python scripts/create_demo_data.py          # Use this instead
streamlit run dashboard/dashboard.py
```

## 📊 Expected Output

After running the pipeline, you should see:

- **Audio chunks**: `audio/*_chunk_*.wav`
- **Transcripts**: `audio/*.txt`
- **Speaker data**: `audio/*.rttm`
- **Stance analysis**: `audio/stance_analysis.json`
- **Final data**: `audio/debate_data.json`
- **Dashboard**: http://localhost:8501
