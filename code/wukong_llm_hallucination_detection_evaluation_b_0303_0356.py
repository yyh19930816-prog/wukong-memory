"""
File: uqlm_demo.py
Source: GitHub repository cvs-health/uqlm (https://github.com/cvs-health/uqlm)
Date: 2023-11-15
Description: Demo implementation of UQLM (Uncertainty Quantification for Language Models)
             showing how to use basic hallucination detection on LLM outputs.
             Simulates the core functionality without actual API calls.
"""

import numpy as np
from typing import List, Dict, Optional, Callable

class UQLMScorer:
    """Base class for different types of UQLM scorers"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        
    def score(self, prompt: str, response: str) -> float:
        """Score the response for likelihood of hallucination (0-1)"""
        raise NotImplementedError

class SemanticEntropyScorer(UQLMScorer):
    """Scorer based on semantic entropy"""
    
    def score(self, prompt: str, response: str) -> float:
        """
        Implement basic semantic entropy scoring.
        Higher score means more confident (less likely to hallucinate)
        """
        # Simulate semantic analysis (would use embeddings in real implementation)
        words = response.split()
        unique_words = set(words)
        
        # Simple heuristic: longer responses with more unique words are penalized
        length_penalty = min(len(words) / 50, 1.0)  # Normalize by max length
        uniqueness_penalty = len(unique_words) / len(words) if words else 0
        
        # Combine factors to get confidence score
        confidence = 0.7 + 0.3 * (1 - uniqueness_penalty) - 0.2 * length_penalty
        return np.clip(confidence, 0, 1)

class ConsistencyScorer(UQLMScorer):
    """Scorer based on response consistency through multiple samples"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", n_samples: int = 3):
        super().__init__(model_name)
        self.n_samples = n_samples
        
    def score(self, prompt: str, response: str) -> float:
        """Score based on simulated consistency checks"""
        # In a real implementation, we'd generate multiple responses
        # Here we simulate variance by adding randomness
        base_score = 0.8 if "accurate" in response.lower() else 0.5
        
        # Add some random variance to simulate sampling
        variance = np.random.normal(0, 0.1, self.n_samples)
        avg_score = np.clip(base_score + np.mean(variance), 0, 1)
        
        return float(avg_score)

class UQLMManager:
    """Main interface for UQLM functionality"""
    
    def __init__(self):
        self.scorers = {
            "semantic_entropy": SemanticEntropyScorer(),
            "consistency": ConsistencyScorer()
        }
        
    def get_scorer(self, scorer_type: str) -> Optional[UQLMScorer]:
        """Get a scorer by type"""
        return self.scorers.get(scorer_type.lower())
    
    def evaluate_response(self, prompt: str, response: str) -> Dict[str, float]:
        """
        Evaluate a response using all available scorers
        Returns dict of scores keyed by scorer type
        """
        return {
            scorer_type: scorer.score(prompt, response)
            for scorer_type, scorer in self.scorers.items()
        }

def main():
    """Demo of UQLM functionality"""
    print("UQLM Demo - Hallucination