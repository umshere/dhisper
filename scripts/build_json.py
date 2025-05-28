#!/usr/bin/env python3
"""
build_json.py - Aggregate ASR, diarization, and stance analysis into unified JSON

This script merges transcription, speaker diarization, and stance analysis
results into a single JSON structure for dashboard consumption.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

def parse_rttm_file(rttm_file: Path) -> List[Dict]:
    """
    Parse RTTM diarization file
    
    Args:
        rttm_file (Path): Path to RTTM file
        
    Returns:
        List[Dict]: Speaker segments with timestamps
    """
    segments = []
    
    try:
        with open(rttm_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 8 and parts[0] == "SPEAKER":
                    segment = {
                        "start_time": float(parts[3]),
                        "duration": float(parts[4]),
                        "end_time": float(parts[3]) + float(parts[4]),
                        "speaker": parts[7]
                    }
                    segments.append(segment)
                    
    except Exception as e:
        print(f"Error parsing RTTM file {rttm_file}: {e}")
        
    return segments

def load_stance_analysis(audio_dir: Path) -> Dict:
    """
    Load stance analysis results
    
    Args:
        audio_dir (Path): Directory containing stance analysis
        
    Returns:
        Dict: Stance analysis results by filename
    """
    stance_file = audio_dir / "stance_analysis.json"
    stance_data = {}
    
    try:
        if stance_file.exists():
            with open(stance_file, 'r') as f:
                results = json.load(f)
                
            for result in results:
                if "error" not in result:
                    stance_data[result["file"]] = {
                        "stance_scores": result["stance_scores"],
                        "dominant_stance": result["dominant_stance"],
                        "text": result["text"]
                    }
                    
    except Exception as e:
        print(f"Error loading stance analysis: {e}")
        
    return stance_data

def extract_chunk_info(filename: str) -> Dict:
    """
    Extract chunk information from filename
    
    Args:
        filename (str): Chunk filename (e.g., "debate_chunk_001.wav")
        
    Returns:
        Dict: Chunk metadata (index, start_time estimate)
    """
    try:
        # Extract chunk number from filename
        parts = filename.replace('.wav', '').replace('.txt', '').replace('.rttm', '').split('_')
        chunk_num = int(parts[-1])
        
        # Estimate start time (10s chunks with 1s overlap = 9s intervals)
        estimated_start = chunk_num * 9
        
        return {
            "chunk_index": chunk_num,
            "estimated_start_time": estimated_start,
            "estimated_end_time": estimated_start + 10
        }
        
    except:
        return {
            "chunk_index": 0,
            "estimated_start_time": 0,
            "estimated_end_time": 10
        }

def merge_chunk_data(audio_dir: Path) -> List[Dict]:
    """
    Merge all data for each audio chunk
    
    Args:
        audio_dir (Path): Directory containing processed files
        
    Returns:
        List[Dict]: Merged chunk data
    """
    # Load stance analysis
    stance_data = load_stance_analysis(audio_dir)
    
    # Find all audio chunks
    wav_files = list(audio_dir.glob("*_chunk_*.wav"))
    chunks = []
    
    for wav_file in sorted(wav_files):
        chunk_name = wav_file.name
        base_name = wav_file.stem
        
        # Get chunk metadata
        chunk_info = extract_chunk_info(chunk_name)
        
        # Load transcription
        txt_file = wav_file.with_suffix('.txt')
        transcription = ""
        if txt_file.exists():
            try:
                transcription = txt_file.read_text().strip()
            except:
                pass
        
        # Load diarization
        rttm_file = wav_file.with_suffix('.rttm')
        speaker_segments = []
        if rttm_file.exists():
            speaker_segments = parse_rttm_file(rttm_file)
        
        # Get stance analysis
        stance_info = stance_data.get(txt_file.name, {})
        
        # Build chunk data
        chunk_data = {
            "chunk_id": base_name,
            "audio_file": chunk_name,
            "chunk_index": chunk_info["chunk_index"],
            "start_time": chunk_info["estimated_start_time"],
            "end_time": chunk_info["estimated_end_time"],
            "transcription": transcription,
            "speaker_segments": speaker_segments,
            "stance_analysis": stance_info,
            "has_transcription": bool(transcription),
            "has_diarization": bool(speaker_segments),
            "has_stance": bool(stance_info)
        }
        
        chunks.append(chunk_data)
    
    return chunks

def build_aggregate_stats(chunks: List[Dict]) -> Dict:
    """
    Build aggregate statistics from chunks
    
    Args:
        chunks (List[Dict]): List of chunk data
        
    Returns:
        Dict: Aggregate statistics
    """
    stats = {
        "total_chunks": len(chunks),
        "total_duration": max([c["end_time"] for c in chunks]) if chunks else 0,
        "chunks_with_transcription": sum(1 for c in chunks if c["has_transcription"]),
        "chunks_with_diarization": sum(1 for c in chunks if c["has_diarization"]),
        "chunks_with_stance": sum(1 for c in chunks if c["has_stance"]),
        "stance_distribution": {"liberal": 0, "conservative": 0, "moderate": 0},
        "speakers": set(),
        "total_text_length": 0
    }
    
    for chunk in chunks:
        # Count stance distribution
        if chunk["has_stance"]:
            dominant_stance = chunk["stance_analysis"].get("dominant_stance", "moderate")
            stats["stance_distribution"][dominant_stance] += 1
        
        # Collect unique speakers
        for segment in chunk["speaker_segments"]:
            stats["speakers"].add(segment["speaker"])
        
        # Sum text length
        stats["total_text_length"] += len(chunk["transcription"])
    
    # Convert speakers set to list
    stats["speakers"] = sorted(list(stats["speakers"]))
    stats["speaker_count"] = len(stats["speakers"])
    
    return stats

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Aggregate ASR, diarization, and stance analysis")
    parser.add_argument("audio_dir", help="Directory containing processed audio chunks")
    parser.add_argument("--output", default="debate_data.json", help="Output JSON filename")
    
    args = parser.parse_args()
    
    # Validate audio directory
    audio_dir = Path(args.audio_dir)
    if not audio_dir.exists():
        print(f"Error: Audio directory {audio_dir} does not exist")
        sys.exit(1)
    
    print(f"Aggregating data from {audio_dir}...")
    
    # Merge chunk data
    chunks = merge_chunk_data(audio_dir)
    
    if not chunks:
        print("No audio chunks found! Make sure you've run the processing pipeline.")
        sys.exit(1)
    
    # Build aggregate statistics
    stats = build_aggregate_stats(chunks)
    
    # Create final data structure
    debate_data = {
        "metadata": {
            "source_directory": str(audio_dir),
            "processed_at": str(Path.cwd()),
            "total_chunks": len(chunks)
        },
        "statistics": stats,
        "chunks": chunks
    }
    
    # Save to JSON
    output_file = audio_dir / args.output
    with open(output_file, 'w') as f:
        json.dump(debate_data, f, indent=2)
    
    print(f"Aggregation complete! Data saved to {output_file}")
    print(f"\nSummary:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Duration: {stats['total_duration']:.1f} seconds")
    print(f"  Speakers: {stats['speaker_count']} ({', '.join(stats['speakers'])})")
    print(f"  Transcribed chunks: {stats['chunks_with_transcription']}")
    print(f"  Diarized chunks: {stats['chunks_with_diarization']}")
    print(f"  Stance analyzed chunks: {stats['chunks_with_stance']}")

if __name__ == "__main__":
    main()
