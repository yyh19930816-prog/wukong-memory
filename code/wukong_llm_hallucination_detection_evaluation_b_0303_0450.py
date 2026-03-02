#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UQLM Uncertainty Quantification Demo Script
Learned from: https://github.com/cvs-health/uqlm
Created: April 2024
Description: Demonstrates core UQLM functionality for LLM hallucination detection
using uncertainty quantification techniques. This simplified version implements
basic semantic similarity scoring as a confidence metric.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine
from typing import Tuple, List


class UQLMScorer:
    """Core UQLM scorer for detecting LLM hallucinations using semantic similarity"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the scorer with a sentence embedding model
        
        Args:
            model_name: Name of the SentenceTransformer model to use
        """
        self.model = SentenceTransformer(model_name)
        
    def calculate_confidence(
        self, 
        query: str, 
        response: str, 
        context: str = None
    ) -> Tuple[float, dict]:
        """
        Calculate confidence score (0-1) for LLM response
        
        Args:
            query: The original user query/prompt
            response: The LLM generated response
            context: Optional context (default None)
            
        Returns:
            Tuple of (confidence_score, debug_info)
        """
        # Encode all texts into embeddings
        texts_to_encode = [t for t in [query, response, context] if t is not None]
        embeddings = self.model.encode(texts_to_encode)
        
        # Get relevant embeddings
        query_embedding = embeddings[0]
        response_embedding = embeddings[1]
        context_embedding = embeddings[2] if context else None
        
        # Calculate primary confidence score (1 - cosine distance)
        confidence = 1 - cosine(query_embedding, response_embedding)
        
        # If context is provided, calculate additional metrics
        debug_info = {"query_response_similarity": confidence}
        if context:
            context_similarity = 1 - cosine(context_embedding, response_embedding)
            debug_info["context_response_similarity"] = context_similarity
            confidence = (confidence + context_similarity) / 2
        
        # Clip confidence to 0-1 range
        confidence = max(0, min(1, confidence))
        
        return confidence, debug_info


def demo():
    """Demonstration of UQLM functionality"""
    
    print("UQLM Demonstration - Hallucination Detection\n")
    
    # Initialize the scorer
    scorer = UQLMScorer()
    
    # Test cases - (query, response, [context])
    test_cases = [
        ("Explain quantum computing", 
         "Quantum computing uses quantum bits or qubits.", 
         "Quantum computing harnesses quantum phenomena like superposition."),
        
        ("Explain quantum computing", 
         "Quantum computers use chocolate chips to perform calculations.", 
         None),
        
        ("What's the capital of France?", 
         "The capital of France is Paris.", 
         None),
        
        ("What's the capital of France?", 
         "The capital of France is Berlin.", 
         None)
    ]
    
    # Evaluate each test case
    for i, (query, response, context) in enumerate(test_cases):
        score, metrics = scorer.calculate_confidence(query, response, context)
        
        print(f"\nTest Case {i+1}:")
        print(f"Query:    {query}")
        print(f"Response: {response}")
        if context:
            print(f"Context:  {context}")
        print(f"\nConfidence Score: {score:.3