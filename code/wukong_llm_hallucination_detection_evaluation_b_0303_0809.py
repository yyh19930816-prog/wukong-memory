#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
uqlm_demo.py
Demo script showcasing Uncertainty Quantification for Language Models functionality
Based on cvs-health/uqlm repository (https://github.com/cvs-health/uqlm)
Created: 2023-11-15

Implements basic hallucination detection for LLM outputs using confidence scoring.
Provides example scorers for measuring uncertainty in model responses.
"""

from typing import List, Tuple, Dict
import numpy as np
from scipy.special import softmax
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class UQLMScorer:
    """Base class for uncertainty quantification scorers"""
    
    def __init__(self, model_name: str = "bert-base-uncased"):
        """
        Initialize scorer with pretrained model
        Args:
            model_name: Name of pretrained model to use
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
    def get_confidence(self, prompt: str, response: str) -> float:
        """
        Compute confidence score between 0-1 for LLM response
        Args:
            prompt: Input prompt given to LLM
            response: Generated response from LLM
        Returns:
            Confidence score (higher = less likely to be hallucination)
        """
        raise NotImplementedError


class SemanticConsistencyScorer(UQLMScorer):
    """Scorer based on semantic consistency between prompt and response"""
    
    def get_confidence(self, prompt: str, response: str) -> float:
        """
        Compute semantic similarity between prompt and response
        Higher similarity scores indicate more consistent responses
        """
        # Encode both texts
        inputs = self.tokenizer([prompt, response], 
                              padding=True, 
                              truncation=True,
                              return_tensors="pt")
        
        # Get embeddings
        outputs = self.model(**inputs, output_hidden_states=True)
        embeddings = outputs.hidden_states[-1].mean(dim=1).detach().numpy()
        
        # Calculate cosine similarity
        similarity = cosine_similarity(embeddings)[0][1]
        
        # Scale to 0-1 range
        return (similarity + 1) / 2


class PerplexityScorer(UQLMScorer):
    """Scorer based on perplexity of the generated response"""
    
    def get_confidence(self, prompt: str, response: str) -> float:
        """
        Compute perplexity-based confidence score
        Lower perplexity indicates more confident responses
        """
        inputs = self.tokenizer(response, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs, labels=inputs["input_ids"])
        loss = outputs.loss
        perplexity = torch.exp(loss).item()
        
        # Convert perplexity to 0-1 scale (inverse relationship)
        max_perplexity = 100  # Rough heuristic cutoff
        return max(0, 1 - (perplexity / max_perplexity))


def demo_uqlm():
    """Demonstrate UQLM functionality with example prompts"""
    examples = [
        ("Explain quantum computing", 
         "Quantum computing uses qubits which can be in superposition of 0 and 1 states."),
        ("Who invented the telephone?",
         "Alexander Graham Bell invented the telephone in 1876."),
        ("Tell me about medieval history",
         "Purple elephants danced on rainbows during medieval times.")
    ]
    
    # Initialize scorers
    semantic_scorer = SemanticConsistencyScorer()
    perplexity_scorer =