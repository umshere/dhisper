#!/usr/bin/env python3
"""
stance.py - Political stance analysis using sentence transformers

This script analyzes political stance of transcribed text using
semantic similarity with political position embeddings.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    print("Error: Required packages not installed")
    print("Install with: pip install sentence-transformers numpy")
    sys.exit(1)

# Political stance reference statements
STANCE_REFERENCES = {
    "liberal": [
        "Government should play a larger role in addressing social inequality",
        "We need stronger environmental regulations to combat climate change",
        "Healthcare is a human right that should be guaranteed by government",
        "Tax the wealthy more to fund social programs",
        "Immigration enriches our society and should be encouraged"
    ],
    "conservative": [
        "Free markets and minimal government intervention drive prosperity",
        "Individual responsibility is more important than government assistance",
        "Traditional values and institutions should be preserved",
        "Lower taxes stimulate economic growth and job creation",
        "Strong national defense and border security are essential"
    ],
    "moderate": [
        "We need balanced solutions that consider multiple perspectives",
        "Both government and private sector have important roles to play",
        "Compromise and bipartisan cooperation are essential for progress",
        "Evidence-based policies should guide decision making",
        "We should focus on what unites us rather than what divides us"
    ]
}

class StanceAnalyzer:
    """Political stance analyzer using sentence transformers"""
    
    def __init__(self, model_path="models/stance-classifier"):
        """
        Initialize stance analyzer
        
        Args:
            model_path (str): Path to sentence transformer model
        """
        try:
            self.model = SentenceTransformer(model_path)
        except:
            print(f"Warning: Could not load local model from {model_path}")
            print("Downloading default model...")
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Pre-compute reference embeddings
        self.reference_embeddings = {}
        for stance, statements in STANCE_REFERENCES.items():
            embeddings = self.model.encode(statements)
            self.reference_embeddings[stance] = np.mean(embeddings, axis=0)
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze political stance of text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict[str, float]: Stance scores (liberal, conservative, moderate)
        """
        if not text.strip():
            return {"liberal": 0.0, "conservative": 0.0, "moderate": 0.0}
        
        # Encode input text
        text_embedding = self.model.encode([text])[0]
        
        # Calculate similarities with reference stances
        similarities = {}
        for stance, ref_embedding in self.reference_embeddings.items():
            similarity = np.dot(text_embedding, ref_embedding) / (
                np.linalg.norm(text_embedding) * np.linalg.norm(ref_embedding)
            )
            similarities[stance] = float(similarity)
        
        # Normalize to probabilities
        total = sum(similarities.values())
        if total > 0:
            similarities = {k: v/total for k, v in similarities.items()}
        
        return similarities

def analyze_transcription_file(txt_file: Path, analyzer: StanceAnalyzer) -> Dict:
    """
    Analyze stance of a transcription file
    
    Args:
        txt_file (Path): Path to transcription text file
        analyzer (StanceAnalyzer): Stance analyzer instance
        
    Returns:
        Dict: Analysis results
    """
    try:
        text = txt_file.read_text().strip()
        if not text:
            return {"error": "Empty transcription"}
        
        stance_scores = analyzer.analyze_text(text)
        
        return {
            "file": txt_file.name,
            "text": text,
            "stance_scores": stance_scores,
            "dominant_stance": max(stance_scores.items(), key=lambda x: x[1])[0]
        }
        
    except Exception as e:
        return {"error": f"Error analyzing {txt_file}: {e}"}

def process_directory(audio_dir: Path, analyzer: StanceAnalyzer):
    """
    Process all transcription files in a directory
    
    Args:
        audio_dir (Path): Directory containing transcription files
        analyzer (StanceAnalyzer): Stance analyzer instance
    """
    txt_files = list(audio_dir.glob("*.txt"))
    
    if not txt_files:
        print(f"No transcription files found in {audio_dir}")
        return
    
    print(f"Found {len(txt_files)} transcription files to analyze")
    
    results = []
    for txt_file in sorted(txt_files):
        print(f"Analyzing {txt_file.name}...")
        result = analyze_transcription_file(txt_file, analyzer)
        results.append(result)
    
    # Save combined results
    output_file = audio_dir / "stance_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Stance analysis complete! Results saved to {output_file}")
    
    # Print summary
    valid_results = [r for r in results if "error" not in r]
    if valid_results:
        stance_counts = {}
        for result in valid_results:
            stance = result["dominant_stance"]
            stance_counts[stance] = stance_counts.get(stance, 0) + 1
        
        print(f"\nStance distribution across {len(valid_results)} files:")
        for stance, count in stance_counts.items():
            percentage = (count / len(valid_results)) * 100
            print(f"  {stance.capitalize()}: {count} files ({percentage:.1f}%)")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Analyze political stance of transcribed text")
    parser.add_argument("audio_dir", help="Directory containing transcription files")
    parser.add_argument("--model-path", default="models/stance-classifier",
                       help="Path to sentence transformer model")
    
    args = parser.parse_args()
    
    # Validate audio directory
    audio_dir = Path(args.audio_dir)
    if not audio_dir.exists():
        print(f"Error: Audio directory {audio_dir} does not exist")
        sys.exit(1)
    
    # Initialize analyzer and process files
    analyzer = StanceAnalyzer(args.model_path)
    process_directory(audio_dir, analyzer)

if __name__ == "__main__":
    main()
