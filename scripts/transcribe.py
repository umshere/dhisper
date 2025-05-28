#!/usr/bin/env python3
"""
transcribe.py - Transcribe audio chunks using whisper.cpp

This script processes all WAV files in a directory using whisper.cpp
and outputs transcription text files alongside the audio.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

def transcribe_audio(audio_file, whisper_path="models/whisper.cpp/main", model_path="models/whisper.cpp/models/ggml-base.en.bin"):
    """
    Transcribe a single audio file using whisper.cpp
    
    Args:
        audio_file (Path): Path to the audio file
        whisper_path (str): Path to whisper.cpp binary
        model_path (str): Path to whisper model file
        
    Returns:
        str: Transcribed text or None if failed
    """
    try:
        # Build whisper.cpp command
        cmd = [
            whisper_path,
            "-m", model_path,
            "-f", str(audio_file),
            "--output-txt",
            "--no-timestamps"
        ]
        
        print(f"Transcribing {audio_file.name}...")
        
        # Run whisper.cpp subprocess
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=audio_file.parent
        )
        
        if result.returncode != 0:
            print(f"Error transcribing {audio_file}: {result.stderr}")
            return None
            
        # Read generated text file
        txt_file = audio_file.with_suffix('.txt')
        if txt_file.exists():
            return txt_file.read_text().strip()
        else:
            print(f"Warning: Expected output file {txt_file} not found")
            return None
            
    except Exception as e:
        print(f"Exception during transcription of {audio_file}: {e}")
        return None

def process_directory(audio_dir, whisper_path, model_path):
    """
    Process all WAV files in a directory
    
    Args:
        audio_dir (Path): Directory containing audio files
        whisper_path (str): Path to whisper.cpp binary
        model_path (str): Path to whisper model
    """
    audio_files = list(audio_dir.glob("*.wav"))
    
    if not audio_files:
        print(f"No WAV files found in {audio_dir}")
        return
        
    print(f"Found {len(audio_files)} audio files to transcribe")
    
    success_count = 0
    for audio_file in sorted(audio_files):
        transcription = transcribe_audio(audio_file, whisper_path, model_path)
        if transcription:
            success_count += 1
            
    print(f"Successfully transcribed {success_count}/{len(audio_files)} files")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Transcribe audio chunks using whisper.cpp")
    parser.add_argument("audio_dir", help="Directory containing audio files to transcribe")
    parser.add_argument("--whisper-path", default="models/whisper.cpp/main", 
                       help="Path to whisper.cpp binary")
    parser.add_argument("--model-path", default="models/whisper.cpp/models/ggml-base.en.bin",
                       help="Path to whisper model file")
    
    args = parser.parse_args()
    
    # Validate paths
    audio_dir = Path(args.audio_dir)
    if not audio_dir.exists():
        print(f"Error: Audio directory {audio_dir} does not exist")
        sys.exit(1)
        
    if not Path(args.whisper_path).exists():
        print(f"Error: Whisper binary {args.whisper_path} not found")
        print("Have you compiled whisper.cpp? Run: cd models/whisper.cpp && make")
        sys.exit(1)
        
    if not Path(args.model_path).exists():
        print(f"Error: Whisper model {args.model_path} not found")
        print("Download model with: bash models/whisper.cpp/models/download-ggml-model.sh base.en")
        sys.exit(1)
    
    # Process audio files
    process_directory(audio_dir, args.whisper_path, args.model_path)

if __name__ == "__main__":
    main()
