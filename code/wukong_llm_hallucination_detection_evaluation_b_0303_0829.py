#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UQLM Uncertainty Quantification Demo Script
Source: GitHub cvs-health/uqlm repository (https://github.com/cvs-health/uqlm)
Created: 2023-11-15
Description: Demonstrates LLM hallucination detection capabilities using UQLM library.
Implements response-level uncertainty scoring for LLM outputs.
"""

from uqlm import (
    SimilarityScorer,
    SemanticEntropyScorer,
    PTrueScorer,
    EccentricityScorer
)
from typing import List, Dict, Any
import numpy as np

class UQLMDemo:
    """Demonstration of UQLM's uncertainty quantification methods."""
    
    def __init__(self):
        """Initialize different types of scorers."""
        self.scorers = {
            'similarity': SimilarityScorer(),
            'semantic_entropy': SemanticEntropyScorer(),
            'ptrue': PTrueScorer(),
            'eccentricity': EccentricityScorer()
        }
    
    def generate_sample_responses(self) -> List[str]:
        """Generate sample LLM responses for demonstration.
        
        Returns:
            List of potential LLM responses including some hallucinations.
        """
        return [
            "The capital of France is Paris.",
            "The capital of France is Lyon.",  # Incorrect
            "Paris serves as France's capital city.",
            "France's main city is Marseille.",  # Incorrect
            "French capital is Paris located in Europe."
        ]
    
    def score_responses(self, responses: List[str]) -> Dict[str, Any]:
        """Score responses using all available UQLM methods.
        
        Args:
            responses: List of LLM responses to evaluate
            
        Returns:
            Dictionary containing scores from each method
        """
        results = {}
        
        # Calculate scores using each method
        for method, scorer in self.scorers.items():
            scores = [scorer.score(response) for response in responses]
            results[method] = {
                'scores': scores,
                'average': np.mean(scores),
                'variance': np.var(scores)
            }
        
        return results
    
    def analyze_results(self, results: Dict[str, Any]) -> None:
        """Analyze and display scoring results.
        
        Args:
            results: Dictionary containing scoring results
        """
        print("\n=== UQLM Uncertainty Scoring Results ===")
        for method, data in results.items():
            print(f"\n{method.replace('_', ' ').title()} Method:")
            print(f"  Average Confidence: {data['average']:.2f}")
            print(f"  Score Variance: {data['variance']:.2f}")
            
            # Print individual scores
            print("  Individual Scores:")
            for i, score in enumerate(data['scores']):
                print(f"    Response {i+1}: {score:.2f}")

def main():
    """Main demo execution."""
    demo = UQLMDemo()
    
    print("=== Generating Sample LLM Responses ===")
    responses = demo.generate_sample_responses()
    for i, response in enumerate(responses):
        print(f"{i+1}. {response}")
    
    print("\n=== Calculating Uncertainty Scores ===")
    results = demo.score_responses(responses)
    
    demo.analyze_results(results)
    
    print("\nNote: Higher scores indicate higher confidence (lower likelihood of hallucination)")

if __name__ == "__main__":
    main()