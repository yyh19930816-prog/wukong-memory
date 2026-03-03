#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UQLM Library Demo Script
Learn Source: GitHub cvs-health/uqlm repository
Date: Current Date
Functionality: Demonstrates core uncertainty quantification capabilities of UQLM
for detecting hallucinations in Large Language Model outputs.
"""

from typing import List
import numpy as np
from scipy.special import softmax

class UQLMScorer:
    """Base class for uncertainty quantification scorers."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize the scorer with a language model.
        
        Args:
            model_name: Name of the language model to use
        """
        self.model_name = model_name
        
    def score(self, prompt: str, response: str) -> float:
        """
        Score a single response for uncertainty/hallucination.
        
        Args:
            prompt: The input prompt given to the LLM
            response: The generated response to score
            
        Returns:
            Confidence score between 0 and 1 (higher is more confident)
        """
        raise NotImplementedError


class SemanticEntropyScorer(UQLMScorer):
    """Scorer that uses semantic entropy to quantify uncertainty."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        super().__init__(model_name)
        
    def _get_response_variations(self, prompt: str, n: int = 5) -> List[str]:
        """
        Generate multiple response variations for entropy calculation.
        In practice this would call the LLM API, but we mock it here.
        
        Args:
            prompt: Input prompt
            n: Number of variations to generate
            
        Returns:
            List of response variations
        """
        # Mock implementation - real version would call LLM API
        base_response = f"Response to: {prompt}"
        return [f"{base_response} variation {i}" for i in range(n)]
    
    def _embed_text(self, text: str) -> np.ndarray:
        """
        Generate semantic embedding for text.
        Mock implementation - real version would use embedding API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Simulate embedding with random values
        return np.random.rand(512)
    
    def score(self, prompt: str, response: str) -> float:
        """
        Calculate semantic entropy score.
        
        Args:
            prompt: Input prompt
            response: Response to evaluate
            
        Returns:
            Confidence score (higher = more confident)
        """
        # Generate response variations
        responses = self._get_response_variations(prompt)
        responses.append(response)  # Include original response
        
        # Calculate embeddings
        embeddings = np.array([self._embed_text(r) for r in responses])
        
        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / norms
        
        # Calculate cosine similarity matrix
        similarity = np.dot(normalized, normalized.T)
        
        # Calculate cluster probabilities (softmax of similarities)
        probs = softmax(similarity, axis=1)
        
        # Calculate entropy (lower entropy = more consistent = higher confidence)
        entropy = -np.sum(probs * np.log(probs + 1e-10)) / len(responses)
        
        # Convert entropy to confidence score (0-1)
        confidence = 1 - entropy / np.log(len(responses))
        
        return float(np.clip(confidence, 0, 1))


if __name__ == "__main__":
    # Demo usage
    scorer = SemanticEntropyScorer()