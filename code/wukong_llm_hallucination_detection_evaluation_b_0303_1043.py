#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Source: https://github.com/cvs-health/uqlm
# Date: 2024-02-20
# Description: Python script demonstrating UQLM's core functionality for LLM
# uncertainty quantification and hallucination detection with HuggingFace models

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict, Tuple
import numpy as np

class UQLMScorer:
    """
    Core uncertainty quantification scorer for Language Models
    
    Implements basic scoring methods described in UQLM's documentation:
    1. Perplexity-based scoring
    2. Semantic consistency scoring
    3. Token probability-based scoring
    """
    
    def __init__(self, model_name: str = "facebook/opt-350m"):
        """
        Initialize UQLM scorer with a pretrained language model
        
        Args:
            model_name: Name or path of HuggingFace model to use
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device)
        self.model.eval()
        
    def perplexity_score(self, text: str) -> float:
        """
        Calculate perplexity-based confidence score (0-1)
        Lower perplexity indicates higher confidence
        
        Args:
            text: Input text to evaluate
            
        Returns:
            Normalized confidence score between 0 (low) and 1 (high)
        """
        encodings = self.tokenizer(text, return_tensors="pt")
        input_ids = encodings.input_ids.to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_ids, labels=input_ids)
            ppl = torch.exp(outputs.loss).item()
            
        # Normalize perplexity to 0-1 range (empirical min/max)
        norm_ppl = max(0, min(1, 1 - (ppl / 100)))
        return norm_ppl
    
    def semantic_score(self, prompt: str, response: str) -> float:
        """
        Calculate semantic consistency score between prompt and response
        
        Args:
            prompt: Original user prompt
            response: Model-generated response
            
        Returns:
            Semantic similarity score (0-1)
        """
        # Simple implementation using Jaccard similarity
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        
        if not prompt_words or not response_words:
            return 0.0
            
        intersection = len(prompt_words & response_words)
        union = len(prompt_words | response_words)
        
        return intersection / union
    
    def token_confidence_score(self, text: str) -> float:
        """
        Calculate average token-level confidence
        
        Args:
            text: Text to evaluate
            
        Returns:
            Average token probability score (0-1)
        """
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            
        # Get probabilities of actual tokens
        token_probs = []
        for i, token_id in enumerate(inputs.input_ids[0][1:]):
            token_probs.append(probs[0, i, token_id].item())
            
        return np.mean(token_probs) if token_probs else 0.0
    
    def composite_score(self, prompt: str, response: str) -> float:
        """
        Calculate composite confidence score combining multiple