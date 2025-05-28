#!/usr/bin/env python3
"""
enhanced_dashboard.py - Unified YouTube Search + Video Player + Real-time Analytics Dashboard

This enhanced dashboard provides a complete integrated experience:
1. YouTube search/URL input interface
2. Embedded video player as centerpiece
3. Real-time analytics updating around the video
4. Live processing status and progress tracking
"""

import json
import time
import threading
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import urllib.parse

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Configure Streamlit page
st.set_page_config(
    page_title="Dhisper - AI Debate Analytics",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better layout
st.markdown("""
<style>
    .main-video-container {
        border: 3px solid #f0f0f0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .analytics-panel {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .processing-status {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 10px;
        margin: 10px 0;
    }
    .transcript-item {
        border-left: 3px solid #ddd;
        padding: 10px;
        margin: 5px 0;
        background-color: #fafafa;
    }
    .current-segment {
        border-left: 3px solid #ff9800;
        background-color: #fff3e0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

class YouTubeProcessor:
    """Handles YouTube video downloading and processing"""
    
    def __init__(self, audio_dir: str = "audio"):
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(exist_ok=True)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        # If it's already just a video ID
        if len(url) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_video_info(self, url: str) -> Dict:
        """Get video information using yt-dlp"""
        try:
            result = subprocess.run([
                'yt-dlp', '--get-title', '--get-duration', '--get-description', url
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                return {
                    'title': lines[0] if len(lines) > 0 else 'Unknown Title',
                    'duration': lines[1] if len(lines) > 1 else 'Unknown Duration',
                    'description': lines[2] if len(lines) > 2 else '',
                    'url': url
                }
        except Exception as e:
            st.error(f"Error getting video info: {e}")
        
        return {}
    
    def download_video(self, url: str, output_name: str = "youtube_video") -> Tuple[bool, Dict]:
        """Download YouTube video and audio"""
        try:
            # Download audio
            audio_cmd = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'wav',
                '--audio-quality', '0',
                '--output', f'{self.audio_dir}/{output_name}.%(ext)s',
                url
            ]
            
            # Download video for playback
            video_cmd = [
                'yt-dlp',
                '--format', 'best[height<=720]',
                '--output', f'{self.audio_dir}/{output_name}_video.%(ext)s',
                url
            ]
            
            # Execute downloads
            audio_result = subprocess.run(audio_cmd, capture_output=True, text=True, timeout=300)
            video_result = subprocess.run(video_cmd, capture_output=True, text=True, timeout=300)
            
            if audio_result.returncode == 0 and video_result.returncode == 0:
                return True, {
                    'audio_file': f'{self.audio_dir}/{output_name}.wav',
                    'video_file': self.find_video_file(output_name)
                }
            else:
                return False, {'error': f'Download failed: {audio_result.stderr}'}
                
        except Exception as e:
            return False, {'error': str(e)}
    
    def find_video_file(self, name_pattern: str) -> Optional[Path]:
        """Find downloaded video file"""
        for ext in ['.mp4', '.mkv', '.webm', '.avi']:
            video_file = self.audio_dir / f"{name_pattern}_video{ext}"
            if video_file.exists():
                return video_file
        return None
    
    def process_audio(self, audio_file: str, progress_callback=None) -> bool:
        """Process audio through the AI pipeline"""
        try:
            steps = [
                (['./scripts/slice_audio.sh', audio_file, 'audio/'], "Slicing audio into chunks..."),
                (['python', 'scripts/transcribe.py', 'audio/'], "Transcribing speech..."),
                (['python', 'scripts/diarise.py', 'audio/'], "Identifying speakers..."),
                (['python', 'scripts/stance.py', 'audio/'], "Analyzing political stance..."),
                (['python', 'scripts/build_json.py', 'audio/'], "Building final dataset...")
            ]
            
            for i, (cmd, description) in enumerate(steps):
                if progress_callback:
                    progress_callback(i / len(steps), description)
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    st.error(f"Processing failed at: {description}\nError: {result.stderr}")
                    return False
            
            if progress_callback:
                progress_callback(1.0, "Processing complete!")
            
            return True
            
        except Exception as e:
            st.error(f"Processing error: {e}")
            return False

def load_debate_data(data_file: Path) -> Dict:
    """Load debate data from JSON file"""
    try:
        if data_file.exists():
            with open(data_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading data: {e}")
    return {}

def create_stance_gauge(stance_scores: Dict[str, float], title: str = "Political Stance") -> go.Figure:
    """Create a stance gauge chart"""
    liberal_score = stance_scores.get("liberal", 0)
    conservative_score = stance_scores.get("conservative", 0)
    moderate_score = stance_scores.get("moderate", 0)
    
    # Calculate position on liberal-conservative spectrum
    if liberal_score + conservative_score > 0:
        position = ((conservative_score - liberal_score) / (liberal_score + conservative_score)) * 50 + 50
    else:
        position = 50  # Neutral
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = position,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 14}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 35], 'color': "lightblue"},
                {'range': [35, 65], 'color': "lightgray"},
                {'range': [65, 100], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    
    fig.update_layout(
        height=200,
        font={'color': "darkblue", 'family': "Arial"},
        margin=dict(l=10, r=10, t=30, b=10)
    )
    
    return fig

def create_timeline_chart(chunks: List[Dict], current_time: float = 0) -> go.Figure:
    """Create timeline chart showing stance over time with current position indicator"""
    timeline_data = []
    
    for chunk in chunks:
        if chunk.get("has_stance"):
            stance_scores = chunk["stance_analysis"]["stance_scores"]
            timeline_data.append({
                "time": chunk["start_time"],
                "liberal": stance_scores.get("liberal", 0),
                "conservative": stance_scores.get("conservative", 0),
                "moderate": stance_scores.get("moderate", 0),
                "text": chunk["transcription"][:50] + "..."
            })
    
    if not timeline_data:
        return go.Figure()
    
    df = pd.DataFrame(timeline_data)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['time'], y=df['liberal'], mode='lines+markers', name='Liberal', 
        line=dict(color='blue', width=2), marker=dict(size=4)
    ))
    fig.add_trace(go.Scatter(
        x=df['time'], y=df['conservative'], mode='lines+markers', name='Conservative', 
        line=dict(color='red', width=2), marker=dict(size=4)
    ))
    fig.add_trace(go.Scatter(
        x=df['time'], y=df['moderate'], mode='lines+markers', name='Moderate', 
        line=dict(color='gray', width=2), marker=dict(size=4)
    ))
    
    # Add current time indicator
    fig.add_vline(x=current_time, line_dash="dash", line_color="orange", line_width=3, 
                  annotation_text="Current")
    
    fig.update_layout(
        title="Political Stance Timeline",
        xaxis_title="Time (seconds)",
        yaxis_title="Stance Score",
        height=300,
        margin=dict(l=10, r=10, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def display_live_transcript(chunks: List[Dict], current_time: float = 0, max_items: int = 8):
    """Display live transcript with current segment highlighting"""
    st.markdown("### 📝 Live Transcript")
    
    if not chunks:
        st.info("Transcript will appear here as video plays...")
        return
    
    # Find chunks around current time
    current_chunks = []
    for chunk in chunks:
        if chunk.get("has_transcription"):
            # Mark current segment
            is_current = chunk["start_time"] <= current_time <= chunk["end_time"]
            chunk["is_current"] = is_current
            current_chunks.append(chunk)
    
    # Sort by time and get recent segments
    current_chunks.sort(key=lambda x: x["start_time"])
    recent_chunks = current_chunks[-max_items:] if len(current_chunks) > max_items else current_chunks
    
    for chunk in reversed(recent_chunks):
        # Determine speaker
        speaker = "Unknown"
        if chunk.get("has_diarization") and chunk["speaker_segments"]:
            speaker = chunk["speaker_segments"][0]["speaker"]
        
        # Get stance for color coding
        stance_icon = "⚪"
        if chunk.get("has_stance"):
            stance = chunk["stance_analysis"]["dominant_stance"]
            stance_icons = {"liberal": "🔵", "conservative": "🔴", "moderate": "⚪"}
            stance_icon = stance_icons.get(stance, "⚪")
        
        # Display segment
        time_str = f"{chunk['start_time']:.0f}s - {chunk['end_time']:.0f}s"
        
        if chunk.get("is_current", False):
            st.markdown(f"""
            <div class="transcript-item current-segment">
                <strong>🎯 CURRENT: {stance_icon} {speaker}</strong> ({time_str})<br>
                <em>{chunk['transcription']}</em>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Add click-to-jump functionality
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button(f"⏯️ {chunk['start_time']:.0f}s", key=f"jump_{chunk.get('chunk_index', 0)}"):
                    st.session_state.video_time = chunk['start_time']
                    st.rerun()
            with col2:
                st.markdown(f"""
                <div class="transcript-item">
                    <strong>{stance_icon} {speaker}</strong> ({time_str})<br>
                    <em>{chunk['transcription']}</em>
                </div>
                """, unsafe_allow_html=True)

def display_speaker_analytics(chunks: List[Dict]):
    """Display compact speaker analytics"""
    st.markdown("### 👥 Speaker Analytics")
    
    # Calculate speaker stats
    speaker_stats = {}
    for chunk in chunks:
        if chunk.get("has_diarization"):
            for segment in chunk["speaker_segments"]:
                speaker = segment["speaker"]
                if speaker not in speaker_stats:
                    speaker_stats[speaker] = {"talk_time": 0, "liberal": 0, "conservative": 0, "moderate": 0, "count": 0}
                
                speaker_stats[speaker]["talk_time"] += segment["duration"]
                speaker_stats[speaker]["count"] += 1
                
                if chunk.get("has_stance"):
                    scores = chunk["stance_analysis"]["stance_scores"]
                    for stance, score in scores.items():
                        speaker_stats[speaker][stance] += score
    
    # Display speaker cards
    for speaker, stats in speaker_stats.items():
        if stats['count'] > 0:
            avg_stance = {k: v/stats['count'] for k, v in stats.items() if k in ['liberal', 'conservative', 'moderate']}
            
            with st.expander(f"🎤 {speaker} ({stats['talk_time']:.1f}s)"):
                mini_gauge = create_stance_gauge(avg_stance, f"{speaker}")
                st.plotly_chart(mini_gauge, use_container_width=True)

def main():
    """Main enhanced dashboard application"""
    st.title("🎙️ Dhisper - AI-Powered YouTube Debate Analytics")
    st.markdown("*Search, analyze, and visualize political debate videos with real-time AI processing*")
    
    # Initialize session state
    if 'video_time' not in st.session_state:
        st.session_state.video_time = 0
    if 'current_video_url' not in st.session_state:
        st.session_state.current_video_url = ""
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = "idle"
    if 'video_info' not in st.session_state:
        st.session_state.video_info = {}
    
    processor = YouTubeProcessor()
    
    # YouTube Search Interface
    st.markdown("## 🔍 YouTube Video Search")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        youtube_url = st.text_input(
            "Enter YouTube URL or Video ID",
            value=st.session_state.current_video_url,
            placeholder="https://youtube.com/watch?v=dQw4w9WgXcQ or dQw4w9WgXcQ",
            help="Paste a YouTube URL or just the video ID"
        )
    
    with col2:
        process_button = st.button("🚀 Load & Process", type="primary")
    
    # Process video if requested
    if process_button and youtube_url:
        # Validate and format URL
        video_id = processor.extract_video_id(youtube_url)
        if not video_id:
            # Maybe it's just a video ID
            if len(youtube_url) == 11 and youtube_url.isalnum():
                video_id = youtube_url
                youtube_url = f"https://youtube.com/watch?v={video_id}"
            else:
                st.error("❌ Invalid YouTube URL. Please check the format.")
                st.stop()
        
        st.session_state.current_video_url = youtube_url
        st.session_state.processing_status = "downloading"
        
        # Get video info
        with st.spinner("Getting video information..."):
            video_info = processor.get_video_info(youtube_url)
            st.session_state.video_info = video_info
        
        if video_info:
            st.success(f"✅ Found: **{video_info['title']}** ({video_info['duration']})")
            
            # Download and process
            with st.spinner("Downloading video and audio..."):
                success, result = processor.download_video(youtube_url, f"youtube_{video_id}")
            
            if success:
                st.success("✅ Download complete!")
                st.session_state.processing_status = "processing"
                
                # Process through AI pipeline
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(progress, message):
                    progress_bar.progress(progress)
                    status_text.text(message)
                
                with st.spinner("Processing through AI pipeline..."):
                    processing_success = processor.process_audio(
                        result['audio_file'], 
                        progress_callback=update_progress
                    )
                
                if processing_success:
                    st.success("🎉 Processing complete! Dashboard loaded below.")
                    st.session_state.processing_status = "complete"
                    st.rerun()
                else:
                    st.error("❌ Processing failed. Check the logs above.")
            else:
                st.error(f"❌ Download failed: {result.get('error', 'Unknown error')}")
    
    # Main Dashboard Layout
    if st.session_state.processing_status == "complete" or Path("audio/debate_data.json").exists():
        st.markdown("---")
        st.markdown("## 📊 Real-time Analytics Dashboard")
        
        # Load current data
        debate_data = load_debate_data(Path("audio/debate_data.json"))
        chunks = debate_data.get("chunks", [])
        stats = debate_data.get("statistics", {})
        
        if not chunks:
            st.warning("No processed data found. Load a video first.")
            return
        
        # Video controls
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            current_time = st.slider(
                "Video Position (seconds)", 
                min_value=0.0, 
                max_value=float(stats.get('total_duration', 100)),
                value=float(st.session_state.video_time),
                step=1.0
            )
            st.session_state.video_time = current_time
        
        with col2:
            if st.button("⏮️ -10s"):
                st.session_state.video_time = max(0, current_time - 10)
                st.rerun()
        with col3:
            if st.button("⏭️ +10s"):
                st.session_state.video_time = current_time + 10
                st.rerun()
        with col4:
            auto_refresh = st.checkbox("🔄 Auto Refresh", value=False)
        
        # Main dashboard layout with video centerpiece
        video_col, analytics_col = st.columns([2, 1])
        
        with video_col:
            st.markdown('<div class="main-video-container">', unsafe_allow_html=True)
            st.markdown("### 📺 Video Player")
            
            # Find and display video
            video_file = processor.find_video_file("youtube_" + processor.extract_video_id(st.session_state.current_video_url) if st.session_state.current_video_url else "youtube_video")
            
            if video_file and video_file.exists():
                with open(video_file, 'rb') as f:
                    video_bytes = f.read()
                st.video(video_bytes, start_time=int(current_time))
            else:
                st.info("Video player will appear here after processing")
            
            # Display video info if available
            if st.session_state.video_info:
                info = st.session_state.video_info
                st.markdown(f"**{info['title']}**")
                st.markdown(f"Duration: {info['duration']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Timeline chart below video
            st.plotly_chart(
                create_timeline_chart(chunks, current_time),
                use_container_width=True
            )
        
        with analytics_col:
            st.markdown('<div class="analytics-panel">', unsafe_allow_html=True)
            
            # Overall stats
            st.metric("📊 Duration", f"{stats.get('total_duration', 0):.1f}s")
            st.metric("🎤 Speakers", stats.get('speaker_count', 0))
            st.metric("📝 Segments", stats.get('total_chunks', 0))
            
            # Overall stance gauge
            if chunks:
                stance_totals = {"liberal": 0, "conservative": 0, "moderate": 0}
                stance_count = 0
                
                for chunk in chunks:
                    if chunk.get("has_stance"):
                        scores = chunk["stance_analysis"]["stance_scores"]
                        for stance, score in scores.items():
                            stance_totals[stance] += score
                        stance_count += 1
                
                if stance_count > 0:
                    avg_stance = {k: v/stance_count for k, v in stance_totals.items()}
                    st.plotly_chart(
                        create_stance_gauge(avg_stance, "Overall Stance"),
                        use_container_width=True
                    )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Bottom section: Live transcript and speaker analytics
        transcript_col, speaker_col = st.columns([2, 1])
        
        with transcript_col:
            display_live_transcript(chunks, current_time)
        
        with speaker_col:
            display_speaker_analytics(chunks)
        
        # Auto-refresh
        if auto_refresh:
            time.sleep(2)
            st.rerun()
    
    elif st.session_state.processing_status == "idle":
        # Show sample videos or instructions
        st.markdown("## 🚀 Quick Start")
        st.markdown("Try these sample political debate videos:")
        
        sample_videos = [
            ("Presidential Debate Highlights", "Sample debate video", "dQw4w9WgXcQ"),
            ("Political Interview", "Analysis-ready content", "dQw4w9WgXcQ"),
            ("Town Hall Discussion", "Multi-speaker format", "dQw4w9WgXcQ")
        ]
        
        cols = st.columns(len(sample_videos))
        for i, (title, desc, video_id) in enumerate(sample_videos):
            with cols[i]:
                st.markdown(f"**{title}**")
                st.markdown(desc)
                if st.button(f"Load Sample {i+1}", key=f"sample_{i}"):
                    st.session_state.current_video_url = f"https://youtube.com/watch?v={video_id}"
                    st.rerun()

if __name__ == "__main__":
    main()
