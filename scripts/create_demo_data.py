#!/usr/bin/env python3
"""
create_demo_data.py - Generate demo data for testing the dashboard

This script creates realistic sample data that mimics the output of the
full processing pipeline, allowing you to test the dashboard immediately.
"""

import json
import random
from pathlib import Path

def generate_demo_data():
    """Generate realistic demo debate data"""
    
    # Demo transcript segments
    demo_segments = [
        {
            "speaker": "SPEAKER_00",
            "text": "I believe we need stronger environmental regulations to combat climate change and protect our planet for future generations.",
            "stance": "liberal"
        },
        {
            "speaker": "SPEAKER_01", 
            "text": "While I agree we need to protect the environment, we must also consider the economic impact on businesses and jobs in traditional industries.",
            "stance": "moderate"
        },
        {
            "speaker": "SPEAKER_00",
            "text": "Healthcare is a fundamental human right, and we should expand Medicare to cover all Americans regardless of their ability to pay.",
            "stance": "liberal"
        },
        {
            "speaker": "SPEAKER_01",
            "text": "Free market solutions and competition between insurance providers will naturally drive down costs and improve quality of care.",
            "stance": "conservative"
        },
        {
            "speaker": "SPEAKER_00",
            "text": "We need to increase taxes on the wealthy and corporations to fund critical social programs and infrastructure investments.",
            "stance": "liberal"
        },
        {
            "speaker": "SPEAKER_01",
            "text": "Lower taxes and reduced government spending will stimulate economic growth and create more opportunities for all Americans.",
            "stance": "conservative"
        },
        {
            "speaker": "SPEAKER_00",
            "text": "Immigration has always been a source of strength for our country, bringing diverse perspectives and valuable skills to our communities.",
            "stance": "liberal"
        },
        {
            "speaker": "SPEAKER_01",
            "text": "We need secure borders and a merit-based immigration system that prioritizes the skills our economy needs most.",
            "stance": "conservative"
        },
        {
            "speaker": "SPEAKER_00",
            "text": "I think we can find common ground on infrastructure spending - it's something that benefits everyone regardless of political affiliation.",
            "stance": "moderate"
        },
        {
            "speaker": "SPEAKER_01",
            "text": "Absolutely, investing in roads, bridges, and broadband is essential for our economic competitiveness and should be a bipartisan priority.",
            "stance": "moderate"
        }
    ]
    
    # Generate stance scores based on predefined stances
    def get_stance_scores(stance_type):
        if stance_type == "liberal":
            return {
                "liberal": random.uniform(0.6, 0.9),
                "conservative": random.uniform(0.05, 0.25), 
                "moderate": random.uniform(0.1, 0.3)
            }
        elif stance_type == "conservative":
            return {
                "liberal": random.uniform(0.05, 0.25),
                "conservative": random.uniform(0.6, 0.9),
                "moderate": random.uniform(0.1, 0.3)
            }
        else:  # moderate
            return {
                "liberal": random.uniform(0.2, 0.4),
                "conservative": random.uniform(0.2, 0.4),
                "moderate": random.uniform(0.4, 0.7)
            }
    
    # Generate chunks
    chunks = []
    for i, segment in enumerate(demo_segments):
        stance_scores = get_stance_scores(segment["stance"])
        
        # Normalize scores to sum to 1
        total = sum(stance_scores.values())
        stance_scores = {k: v/total for k, v in stance_scores.items()}
        
        chunk = {
            "chunk_id": f"demo_chunk_{i:03d}",
            "audio_file": f"demo_chunk_{i:03d}.wav",
            "chunk_index": i,
            "start_time": i * 9,  # 9 second intervals (10s chunks with 1s overlap)
            "end_time": i * 9 + 10,
            "transcription": segment["text"],
            "speaker_segments": [
                {
                    "start_time": 0.0,
                    "duration": 8.5,
                    "end_time": 8.5,
                    "speaker": segment["speaker"]
                }
            ],
            "stance_analysis": {
                "stance_scores": stance_scores,
                "dominant_stance": segment["stance"],
                "text": segment["text"]
            },
            "has_transcription": True,
            "has_diarization": True,
            "has_stance": True
        }
        chunks.append(chunk)
    
    # Calculate aggregate statistics
    total_duration = max(c["end_time"] for c in chunks) if chunks else 0
    speakers = list(set(seg["speaker"] for chunk in chunks for seg in chunk["speaker_segments"]))
    
    stance_counts = {"liberal": 0, "conservative": 0, "moderate": 0}
    for chunk in chunks:
        if chunk["has_stance"]:
            dominant = chunk["stance_analysis"]["dominant_stance"]
            stance_counts[dominant] += 1
    
    stats = {
        "total_chunks": len(chunks),
        "total_duration": total_duration,
        "chunks_with_transcription": len(chunks),
        "chunks_with_diarization": len(chunks),
        "chunks_with_stance": len(chunks),
        "stance_distribution": stance_counts,
        "speakers": speakers,
        "speaker_count": len(speakers),
        "total_text_length": sum(len(c["transcription"]) for c in chunks)
    }
    
    # Create final data structure
    debate_data = {
        "metadata": {
            "source_directory": "audio/",
            "processed_at": "demo_mode",
            "total_chunks": len(chunks),
            "note": "This is demo data generated for testing purposes"
        },
        "statistics": stats,
        "chunks": chunks
    }
    
    return debate_data

def main():
    """Generate demo data and save to file"""
    print("Generating demo debate data...")
    
    # Ensure audio directory exists
    audio_dir = Path("audio")
    audio_dir.mkdir(exist_ok=True)
    
    # Generate data
    demo_data = generate_demo_data()
    
    # Save to JSON file
    output_file = audio_dir / "debate_data.json"
    with open(output_file, 'w') as f:
        json.dump(demo_data, f, indent=2)
    
    print(f"Demo data generated successfully!")
    print(f"Saved to: {output_file}")
    print(f"\nDemo includes:")
    print(f"  - {demo_data['statistics']['total_chunks']} audio chunks")
    print(f"  - {demo_data['statistics']['speaker_count']} speakers: {', '.join(demo_data['statistics']['speakers'])}")
    print(f"  - {demo_data['statistics']['total_duration']:.1f} seconds of debate")
    print(f"  - Stance distribution: {demo_data['statistics']['stance_distribution']}")
    print(f"\nTo view the dashboard:")
    print(f"  streamlit run dashboard/dashboard.py")
    print(f"\nThen open: http://localhost:8501")

if __name__ == "__main__":
    main()
