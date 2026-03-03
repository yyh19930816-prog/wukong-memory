#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UQLM Uncertainty Quantification Demo
Source: GitHub cvs-health/uqlm (https://github.com/cvs-health/uqlm)
Date: 2024-02-20
Description: Demonstrates hallucination detection in LLM outputs using uncertainty quantification techniques.
             Implements basic scorers that analyze response consistency and confidence.
"""

import numpy as np
from typing import List, Dict, Callable
from scipy.special import softmax
from transformers import AutoModelForCausalLM, AutoTokenizer

class UQLMScorer:
    """
    Base class for uncertainty quantification scorers.
    Provides common functionality for measuring LLM response reliability.
    """
    
    def __init__(self, model_name: str = "gpt2"):
        """
        Initialize scorer with a base LLM.
        
        Args:
            model_name: HuggingFace model identifier (default: 'gpt2')
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
    def __call__(self, prompt: str, response: str) -> float:
        """Base scoring method to be implemented by subclasses"""
        raise NotImplementedError

class SemanticConsistencyScorer(UQLMScorer):
    """
    Measures semantic consistency between prompt and response.
    Higher scores indicate better alignment with the prompt.
    """
    
    def __call__(self, prompt: str, response: str) -> float:
        """
        Calculate semantic consistency score.
        
        Args:
            prompt: Input text given to LLM
            response: Generated LLM output
            
        Returns:
            Float score between 0 (inconsistent) and 1 (consistent)
        """
        # Tokenize prompt and response
        prompt_tokens = self.tokenizer.encode(prompt, return_tensors='pt')
        response_tokens = self.tokenizer.encode(response, return_tensors='pt')
        
        # Calculate probability of response given prompt
        with torch.no_grad():
            outputs = self.model(input_ids=prompt_tokens, labels=response_tokens)
            
        # Convert loss to probability-like score
        loss = outputs.loss.item()
        return np.exp(-loss)

class ResponseConfidenceScorer(UQLMScorer):
    """
    Measures confidence of the generated response using token probabilities.
    Higher scores indicate more confident generations.
    """
    
 def __call__(self, prompt: str, response: str) -> float:
        """
        Calculate average token confidence score.
        
        Args:
            prompt: Input text given to LLM
            response: Generated LLM output
            
        Returns:
            Float score between 0 (uncertain) and 1 (certain)
        """
        inputs = self.tokenizer(prompt + response, return_tensors='pt')
        input_ids = inputs['input_ids']
        
        with torch.no_grad():
            logits = self.model(**inputs).logits
            
        # Calculate softmax probabilities
        probs = softmax(logits[0], axis=-1)
        
        # Get probabilities of actual generated tokens
        token_probs = probs[np.arange(len(input_ids[0])-1), input_ids[0][1:]]
        
        # Return geometric mean probability
        return np.exp(np.mean(np.log(token_probs.numpy())))

def main():
    """Demo of UQLM hallucination detection"""
    import torch
    
    # Example prompt and responses (one good, one potentially hallucinated)
    prompt = "Explain the theory of relativity"
    good_response = "The theory of relativity consists of special and general relativity developed by Einstein."
    bad_response = "The