#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uqlm_example.py - Basic example of Uncertainty Quantification for Language Models

Implementation based on GitHub repository: cvs-health/uqlm
Learned Date: 2024-04-01 
Core Functionality: Demonstrate LLM hallucination detection using UQLM confidence scoring

Requirements:
- Python 3.10+
- Install package: pip install uqlm transformers torch
"""
from uqlm.scorers import (
    SemanticEntropyScorer,
    PTrueScorer,
    EnsembleScorer,
    LexicalSimilarityScorer
)
from transformers import pipeline

def main():
    """
    Demonstrates UQLM's core functionality for detecting LLM hallucinations.
    Shows different scoring methods with their execution times.
    """
    # Initialize LLM pipeline (using small model for demo purposes)
    generator = pipeline("text-generation", model="gpt2", device="cpu")
    
    # Sample prompt and LLM responses (one good, one potentially hallucinated)
    prompt = "Explain the theory of relativity"
    good_response = """The theory of relativity consists of two main parts: special relativity 
    and general relativity. Special relativity deals with physics in the absence of gravity, 
    while general relativity explains gravitation."""
    bad_response = """The theory of relativity was invented by Thomas Edison in 1925 when 
    he noticed light bending around his new tungsten light bulbs."""
    
    # Initialize UQLM scorers
    scorers = {
        "Semantic Entropy": SemanticEntropyScorer(generator),
        "P(True)": PTrueScorer(generator),
        "Ensemble": EnsembleScorer(generator),
        "Lexical Similarity": LexicalSimilarityScorer()
    }
    
    # Score both responses
    print(f"\nEvaluating prompt: '{prompt}'\n")
    for name, response in [("Good Response", good_response), ("Bad Response", bad_response)]:
        print(f"\n{name}: '{response}'")
        print("-" * 50)
        
        for scorer_name, scorer in scorers.items():
            try:
                confidence = scorer.score(prompt, response)
                print(f"{scorer_name}: {confidence:.2f}")
            except Exception as e:
                print(f"{scorer_name} failed: {str(e)}")

if __name__ == "__main__":
    main()