#!/usr/bin/env python3
"""
dashboard.py - Real-time debate analytics dashboard with video sync

This dashboard displays live transcripts, stance gauges, speaker analytics,
and synchronized video playback from processed debate audio chunks.
"""

import json
import time
from pathlib import Path
from typing import Dict, List
import base64

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

def load_debate_data(data_file: Path) -> Dict:
    """
    Load debate data from JSON file
    
    Args:
        data_file (Path): Path to aggregated debate data
        
    Returns:
        Dict: Debate data or empty dict if not found
    """
    try:
        if data_file.exists():
            with open(data_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading data: {e}")
    
    return {}

def find_video_file(audio_dir: Path) -> Path:
    """
    Find video file in audio directory
    
    Args:
        audio_dir (Path): Directory containing video files
        
    Returns:
        Path: Path to video file or None if not found
    """
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm']
    
    for ext in video_extensions:
        for video_file in audio_dir.glob(f"*_video{ext}"):
            return video_file
        for video_file in audio_dir.glob(f"*{ext}"):
            return video_file
    
    return None

def display_video_player(video_file: Path, current_time: float = 0):
    """
    Display video player with current time sync
    
    Args:
        video_file (Path): Path to video file
        current_time (float): Current playback time in seconds
    """
    if video_file and video_file.exists():
        st.subheader("📺 Video Player")
        
        # Use Streamlit's video component
        with open(video_file, 'rb') as f:
            video_bytes = f.read()
        
        st.video(video_bytes, start_time=int(current_time))
        
        # Add playback controls
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⏮️ -10s"):
                st.session_state.video_time = max(0, current_time - 10)
        with col2:
            if st.button("⏯️ Play/Pause"):
                st.session_state.video_playing = not st.session_state.get('video_playing', False)
        with col3:
            if st.button("⏭️ +10s"):
                st.session_state.video_time = current_time + 10
    else:
        st.info("📺 No video file found. Add a video to enable synchronized playback.")
        st.markdown("**To add video:**")
        st.code("""
# Download from YouTube
scripts/download_youtube.sh "https://youtube.com/watch?v=VIDEO_ID"

# Or copy existing video
cp your_video.mp4 audio/debate_video.mp4
        """)

def create_stance_gauge(stance_scores: Dict[str, float], title: str = "Political Stance") -> go.Figure:
    """
    Create a stance gauge chart
    
    Args:
        stance_scores (Dict[str, float]): Stance scores
        title (str): Chart title
        
    Returns:
        go.Figure: Plotly gauge figure
    """
    # Convert to liberal-conservative scale (0 to 100)
    liberal_score = stance_scores.get("liberal", 0)
    conservative_score = stance_scores.get("conservative", 0)
    moderate_score = stance_scores.get("moderate", 0)
    
    # Calculate position on liberal-conservative spectrum
    if liberal_score + conservative_score > 0:
        position = ((conservative_score - liberal_score) / (liberal_score + conservative_score)) * 50 + 50
    else:
        position = 50  # Neutral
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = position,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 16}},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 35], 'color': "lightblue", 'name': 'Liberal'},
                {'range': [35, 65], 'color': "lightgray", 'name': 'Moderate'},
                {'range': [65, 100], 'color': "lightcoral", 'name': 'Conservative'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        font={'color': "darkblue", 'family': "Arial"},
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_timeline_chart(chunks: List[Dict]) -> go.Figure:
    """
    Create timeline chart showing stance over time with video sync
    
    Args:
        chunks (List[Dict]): Debate chunks
        
    Returns:
        go.Figure: Plotly timeline figure
    """
    timeline_data = []
    
    for chunk in chunks:
        if chunk.get("has_stance"):
            stance_scores = chunk["stance_analysis"]["stance_scores"]
            timeline_data.append({
                "time": chunk["start_time"],
                "liberal": stance_scores.get("liberal", 0),
                "conservative": stance_scores.get("conservative", 0),
                "moderate": stance_scores.get("moderate", 0),
                "chunk_id": chunk["chunk_id"],
                "text": chunk["transcription"][:50] + "..." if len(chunk["transcription"]) > 50 else chunk["transcription"]
            })
    
    if not timeline_data:
        return go.Figure()
    
    df = pd.DataFrame(timeline_data)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['time'], 
        y=df['liberal'], 
        mode='lines+markers', 
        name='Liberal', 
        line=dict(color='blue', width=3),
        hovertemplate='<b>Liberal</b><br>Time: %{x}s<br>Score: %{y:.2f}<br>%{text}<extra></extra>',
        text=df['text']
    ))
    fig.add_trace(go.Scatter(
        x=df['time'], 
        y=df['conservative'], 
        mode='lines+markers', 
        name='Conservative', 
        line=dict(color='red', width=3),
        hovertemplate='<b>Conservative</b><br>Time: %{x}s<br>Score: %{y:.2f}<br>%{text}<extra></extra>',
        text=df['text']
    ))
    fig.add_trace(go.Scatter(
        x=df['time'], 
        y=df['moderate'], 
        mode='lines+markers', 
        name='Moderate', 
        line=dict(color='gray', width=3),
        hovertemplate='<b>Moderate</b><br>Time: %{x}s<br>Score: %{y:.2f}<br>%{text}<extra></extra>',
        text=df['text']
    ))
    
    # Add current time indicator
    current_time = st.session_state.get('video_time', 0)
    fig.add_vline(x=current_time, line_dash="dash", line_color="orange", line_width=2)
    
    fig.update_layout(
        title="🎯 Political Stance Evolution Over Time",
        xaxis_title="Time (seconds)",
        yaxis_title="Stance Score",
        height=400,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def display_transcript(chunks: List[Dict], max_chunks: int = 10, current_time: float = 0):
    """
    Display scrolling transcript with speaker labels and video sync
    
    Args:
        chunks (List[Dict]): Debate chunks
        max_chunks (int): Maximum chunks to display
        current_time (float): Current video time for highlighting
    """
    st.subheader("📝 Live Transcript")
    
    # Filter chunks around current time
    relevant_chunks = []
    for chunk in chunks:
        if chunk.get("has_transcription"):
            # Highlight current segment
            if chunk["start_time"] <= current_time <= chunk["end_time"]:
                chunk["is_current"] = True
            else:
                chunk["is_current"] = False
            relevant_chunks.append(chunk)
    
    # Sort by time and take recent chunks
    relevant_chunks.sort(key=lambda x: x["start_time"])
    recent_chunks = relevant_chunks[-max_chunks:] if len(relevant_chunks) > max_chunks else relevant_chunks
    
    for chunk in reversed(recent_chunks):  # Most recent first
        if chunk.get("has_transcription"):
            # Determine speaker from diarization
            speaker = "Unknown"
            if chunk.get("has_diarization") and chunk["speaker_segments"]:
                speaker = chunk["speaker_segments"][0]["speaker"]
            
            # Get stance for color coding
            stance = "moderate"
            if chunk.get("has_stance"):
                stance = chunk["stance_analysis"]["dominant_stance"]
            
            # Color code by stance
            stance_colors = {
                "liberal": "🔵",
                "conservative": "🔴", 
                "moderate": "⚪"
            }
            
            color_icon = stance_colors.get(stance, "⚪")
            
            # Highlight current segment
            if chunk.get("is_current", False):
                st.markdown(f"### 🎯 **CURRENT SEGMENT**")
                st.markdown(f"**{color_icon} {speaker}** ({chunk['start_time']:.0f}s-{chunk['end_time']:.0f}s)")
                st.markdown(f"🔊 _{chunk['transcription']}_")
                if chunk.get("has_stance"):
                    scores = chunk["stance_analysis"]["stance_scores"]
                    st.markdown(f"**Stance**: Liberal {scores['liberal']:.2f} | Conservative {scores['conservative']:.2f} | Moderate {scores['moderate']:.2f}")
                st.markdown("---")
            else:
                # Regular display
                time_str = f"{chunk['start_time']:.0f}s"
                if st.button(f"⏯️ Jump to {time_str}", key=f"jump_{chunk['chunk_index']}"):
                    st.session_state.video_time = chunk['start_time']
                    st.rerun()
                
                st.markdown(f"**{color_icon} {speaker}** ({time_str})")
                st.markdown(f"_{chunk['transcription']}_")
                st.markdown("---")

def display_speaker_analytics(chunks: List[Dict]):
    """
    Display speaker analytics panel
    
    Args:
        chunks (List[Dict]): Debate chunks
    """
    st.subheader("👥 Speaker Analytics")
    
    # Calculate speaker statistics
    speaker_stats = {}
    
    for chunk in chunks:
        if chunk.get("has_diarization"):
            for segment in chunk["speaker_segments"]:
                speaker = segment["speaker"]
                if speaker not in speaker_stats:
                    speaker_stats[speaker] = {
                        "talk_time": 0,
                        "chunks": 0,
                        "liberal_score": 0,
                        "conservative_score": 0,
                        "moderate_score": 0
                    }
                
                speaker_stats[speaker]["talk_time"] += segment["duration"]
                speaker_stats[speaker]["chunks"] += 1
                
                # Add stance scores if available
                if chunk.get("has_stance"):
                    scores = chunk["stance_analysis"]["stance_scores"]
                    speaker_stats[speaker]["liberal_score"] += scores.get("liberal", 0)
                    speaker_stats[speaker]["conservative_score"] += scores.get("conservative", 0)
                    speaker_stats[speaker]["moderate_score"] += scores.get("moderate", 0)
    
    # Display speaker cards
    if speaker_stats:
        cols = st.columns(min(len(speaker_stats), 3))
        
        for idx, (speaker, stats) in enumerate(speaker_stats.items()):
            with cols[idx % 3]:
                st.metric(
                    label=f"🎤 {speaker}",
                    value=f"{stats['talk_time']:.1f}s",
                    delta=f"{stats['chunks']} segments"
                )
                
                # Average stance scores
                if stats['chunks'] > 0:
                    avg_liberal = stats['liberal_score'] / stats['chunks']
                    avg_conservative = stats['conservative_score'] / stats['chunks']
                    avg_moderate = stats['moderate_score'] / stats['chunks']
                    
                    # Create mini gauge for this speaker
                    speaker_stance = {
                        "liberal": avg_liberal,
                        "conservative": avg_conservative,
                        "moderate": avg_moderate
                    }
                    
                    mini_gauge = create_stance_gauge(speaker_stance, f"{speaker} Stance")
                    mini_gauge.update_layout(height=200)
                    st.plotly_chart(mini_gauge, use_container_width=True)

def main():
    """Main dashboard application"""
    st.title("🎙️ Dhisper - AI-Powered Debate Analytics")
    st.markdown("*Real-time analysis of political debate audio with AI-powered transcription, diarization, and stance detection*")
    
    # Initialize session state
    if 'video_time' not in st.session_state:
        st.session_state.video_time = 0
    if 'video_playing' not in st.session_state:
        st.session_state.video_playing = False
    
    # Sidebar controls
    st.sidebar.header("⚙️ Controls")
    
    data_file = st.sidebar.text_input(
        "Data File Path", 
        value="audio/debate_data.json",
        help="Path to aggregated debate data JSON file"
    )
    
    auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 30, 5)
    
    # Video time control
    current_time = st.sidebar.number_input(
        "Video Time (seconds)", 
        min_value=0.0, 
        value=float(st.session_state.video_time),
        step=1.0,
        help="Current video playback time"
    )
    st.session_state.video_time = current_time
    
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    
    # Load debate data
    debate_data = load_debate_data(Path(data_file))
    
    if not debate_data:
        st.warning(f"No data found at {data_file}. Make sure you've run the processing pipeline.")
        st.code("""
# To generate demo data:
python scripts/create_demo_data.py

# To process YouTube video:
scripts/download_youtube.sh "https://youtube.com/watch?v=VIDEO_ID"
./scripts/slice_audio.sh audio/youtube_video.wav
python scripts/transcribe.py audio/
python scripts/diarise.py audio/
python scripts/stance.py audio/
python scripts/build_json.py audio/
        """)
        return
    
    # Extract data
    chunks = debate_data.get("chunks", [])
    stats = debate_data.get("statistics", {})
    
    # Find video file
    audio_dir = Path(data_file).parent
    video_file = find_video_file(audio_dir)
    
    # Main dashboard layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total Duration", f"{stats.get('total_duration', 0):.1f}s")
    with col2:
        st.metric("🎤 Speakers", stats.get('speaker_count', 0))
    with col3:
        st.metric("📝 Processed Chunks", stats.get('total_chunks', 0))
    
    # Video and stance overview
    if chunks:
        # Calculate overall stance distribution
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
            
            # Main layout with video
            video_col, chart_col = st.columns([1, 2])
            
            with video_col:
                display_video_player(video_file, current_time)
                
                # Overall stance gauge
                st.plotly_chart(
                    create_stance_gauge(avg_stance, "Overall Debate Stance"),
                    use_container_width=True
                )
            
            with chart_col:
                st.plotly_chart(
                    create_timeline_chart(chunks),
                    use_container_width=True
                )
    
    # Display transcript and speaker analytics
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_transcript(chunks, current_time=current_time)
    
    with col2:
        display_speaker_analytics(chunks)
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
