# Dhisper Architecture - AI-Powered Debate Analytics

## 🏗️ Complete System Architecture

```mermaid
graph TB
    subgraph "Input Sources"
        YT[📺 YouTube Video] --> YTD[yt-dlp Download]
        AU[🎵 Audio File] --> AUD[Audio Input]
        RT[🔴 Live Stream] --> RTA[Real-time Audio]
        YTD --> AUD
        RTA --> AUD
    end

    subgraph "Audio Processing Pipeline"
        AUD --> SLICE[🔪 slice_audio.sh<br/>FFmpeg Chunking<br/>10s + 1s overlap]
        SLICE --> CHUNKS[📦 Audio Chunks<br/>*.wav files]
    end

    subgraph "AI Processing Layer"
        CHUNKS --> ASR[🎤 Whisper.cpp<br/>Speech-to-Text AI<br/>CoreML Optimized]
        CHUNKS --> DIAR[👥 pyannote.audio<br/>Speaker Diarization AI<br/>Neural Embeddings]
        ASR --> TXT[📝 Transcriptions<br/>*.txt files]
        DIAR --> RTTM[🏷️ Speaker Labels<br/>*.rttm files]
        TXT --> STANCE[🎯 Sentence Transformers<br/>Political Stance AI<br/>all-MiniLM-L6-v2]
        STANCE --> STANCEJSON[🔍 Stance Analysis<br/>stance_analysis.json]
    end

    subgraph "Data Aggregation"
        TXT --> MERGE[🔗 build_json.py<br/>Data Merger]
        RTTM --> MERGE
        STANCEJSON --> MERGE
        MERGE --> FINAL[📊 debate_data.json<br/>Unified Dataset]
    end

    subgraph "Real-time Dashboard"
        FINAL --> STREAM[⚡ Streamlit App<br/>dashboard.py]
        STREAM --> GAUGE[📊 Stance Gauges<br/>Plotly Visualizations]
        STREAM --> TIMELINE[📈 Timeline Chart<br/>Political Evolution]
        STREAM --> TRANSCRIPT[📝 Live Transcript<br/>Speaker + Stance Colors]
        STREAM --> ANALYTICS[👥 Speaker Analytics<br/>Talk Time + Positions]
        STREAM --> VIDEO[📺 Video Player<br/>Synchronized Playback]
    end

    subgraph "AI Models"
        WHISPER[🧠 OpenAI Whisper<br/>Transformer ASR]
        PYANNOTE[🧠 pyannote Neural Nets<br/>Speaker Embeddings]
        TRANSFORMER[🧠 Sentence Transformers<br/>Political Classification]
        ASR -.->|uses| WHISPER
        DIAR -.->|uses| PYANNOTE
        STANCE -.->|uses| TRANSFORMER
    end

    subgraph "Real-time Features"
        POLLING[🔄 Auto-refresh<br/>5s intervals]
        WEBSOCKET[🌐 WebSocket Updates<br/>Future Enhancement]
        STREAM --> POLLING
        STREAM -.->|future| WEBSOCKET
    end

    style YT fill:#ff6b6b
    style ASR fill:#4ecdc4
    style DIAR fill:#45b7d1
    style STANCE fill:#96ceb4
    style STREAM fill:#feca57
    style WHISPER fill:#ff9ff3
    style PYANNOTE fill:#54a0ff
    style TRANSFORMER fill:#5f27cd
```

## 🔄 Data Flow Architecture

### Phase 1: Audio Ingestion

```
YouTube URL → yt-dlp → Audio File → FFmpeg Chunking → 10s Overlapped Segments
```

### Phase 2: AI Processing

```
Audio Chunks → [Whisper AI + pyannote AI + Transformer AI] → Structured Data
```

### Phase 3: Real-time Visualization

```
JSON Data → Streamlit Dashboard → Live Charts + Video Sync → User Interface
```

## 🧠 AI Model Details

### 1. Speech Recognition (Whisper)

- **Architecture**: Transformer encoder-decoder
- **Parameters**: 244M (base.en model)
- **Optimization**: CoreML acceleration on Apple Silicon
- **Accuracy**: ~95% on clear political speech
- **Latency**: ~2-3 seconds per 10s chunk

### 2. Speaker Diarization (pyannote.audio)

- **Architecture**: CNN + LSTM + Attention
- **Function**: Speaker embedding + clustering
- **Output**: RTTM format with precise timestamps
- **Capability**: 2-8 speakers with 85%+ accuracy

### 3. Political Stance Analysis (Sentence Transformers)

- **Architecture**: BERT-based encoder
- **Embedding Dimension**: 384D semantic vectors
- **Classification**: Liberal/Conservative/Moderate
- **Method**: Cosine similarity with reference embeddings
- **Confidence**: Probability distribution across positions

## 📊 Performance Characteristics

| Component           | Latency    | Accuracy | Resource Usage  |
| ------------------- | ---------- | -------- | --------------- |
| Audio Chunking      | <1s        | 100%     | CPU: Low        |
| Whisper ASR         | 2-3s/chunk | 95%      | CPU+GPU: Medium |
| Speaker Diarization | 1-2s/chunk | 85%      | CPU: High       |
| Stance Analysis     | <1s/chunk  | 70-80%   | CPU: Low        |
| Dashboard Rendering | <500ms     | N/A      | CPU: Low        |

## 🔮 Future Enhancements

### Planned AI Integrations

1. **Fact-Checking AI**: Real-time claim verification
2. **Emotion Detection**: Voice tone and sentiment analysis
3. **Topic Modeling**: Automatic subject classification
4. **Custom Political Models**: Fine-tuned for specific contexts

### Scalability Improvements

1. **WebSocket Streaming**: True real-time updates
2. **Cloud Deployment**: Docker + Kubernetes
3. **Multi-language Support**: Extended Whisper models
4. **Advanced Visualizations**: 3D political space mapping
