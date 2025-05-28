#!/usr/bin/env python3
"""
diarise.py - Speaker diarization using pyannote.audio

This script performs speaker diarization on audio files and outputs
RTTM format files with speaker timestamps.
"""

import argparse
import sys
import warnings
from pathlib import Path

# Suppress pyannote warnings
warnings.filterwarnings("ignore")

try:
    from pyannote.audio import Pipeline
    from pyannote.core import Annotation
except ImportError:
    print("Error: pyannote.audio not installed")
    print("Install with: pip install pyannote.audio")
    sys.exit(1)

def load_diarization_pipeline():
    """
    Load the speaker diarization pipeline
    
    Returns:
        Pipeline: Configured diarization pipeline
    """
    try:
        # Load pre-trained speaker diarization pipeline
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization@2.1",
            use_auth_token=True  # Requires HuggingFace token
        )
        return pipeline
    except Exception as e:
        print(f"Error loading diarization pipeline: {e}")
        print("Make sure you have a HuggingFace token configured:")
        print("1. Visit https://huggingface.co/pyannote/segmentation")
        print("2. Accept the user agreement")
        print("3. Set HF_TOKEN environment variable")
        sys.exit(1)

def diarize_audio(audio_file, pipeline):
    """
    Perform speaker diarization on a single audio file
    
    Args:
        audio_file (Path): Path to the audio file
        pipeline (Pipeline): Diarization pipeline
        
    Returns:
        Annotation: Diarization results
    """
    try:
        print(f"Diarizing {audio_file.name}...")
        
        # Apply diarization pipeline
        diarization = pipeline(str(audio_file))
        
        return diarization
        
    except Exception as e:
        print(f"Error diarizing {audio_file}: {e}")
        return None

def save_rttm(diarization, output_file):
    """
    Save diarization results in RTTM format
    
    Args:
        diarization (Annotation): Diarization results
        output_file (Path): Output RTTM file path
    """
    with open(output_file, 'w') as f:
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            # RTTM format: SPEAKER filename 1 start_time duration <NA> <NA> speaker <NA> <NA>
            f.write(f"SPEAKER {output_file.stem} 1 {segment.start:.3f} {segment.duration:.3f} <NA> <NA> {speaker} <NA> <NA>\n")

def process_directory(audio_dir):
    """
    Process all WAV files in a directory
    
    Args:
        audio_dir (Path): Directory containing audio files
    """
    # Load diarization pipeline once
    pipeline = load_diarization_pipeline()
    
    audio_files = list(audio_dir.glob("*.wav"))
    
    if not audio_files:
        print(f"No WAV files found in {audio_dir}")
        return
        
    print(f"Found {len(audio_files)} audio files to diarize")
    
    success_count = 0
    for audio_file in sorted(audio_files):
        diarization = diarize_audio(audio_file, pipeline)
        
        if diarization is not None:
            # Save RTTM file
            rttm_file = audio_file.with_suffix('.rttm')
            save_rttm(diarization, rttm_file)
            print(f"Saved diarization to {rttm_file}")
            success_count += 1
            
    print(f"Successfully diarized {success_count}/{len(audio_files)} files")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Perform speaker diarization using pyannote.audio")
    parser.add_argument("audio_dir", help="Directory containing audio files to diarize")
    
    args = parser.parse_args()
    
    # Validate audio directory
    audio_dir = Path(args.audio_dir)
    if not audio_dir.exists():
        print(f"Error: Audio directory {audio_dir} does not exist")
        sys.exit(1)
    
    # Process audio files
    process_directory(audio_dir)

if __name__ == "__main__":
    main()
