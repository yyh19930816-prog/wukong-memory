# UQLM (Uncertainty Quantification for Language Models) Implementation
# Source: https://github.com/cvs-health/uqlm
# Date: 2024-03-20
# Description: Demonstrates LLM hallucination detection using uncertainty quantification

import numpy as np
from typing import List, Dict, Union, Callable
from scipy.special import softmax

class UQLMScorer:
    """Base class for UQ scorers that quantify LLM output uncertainty"""
    
    def __init__(self, model_name: str = "gpt2"):
        """
        Initialize scorer with a base language model
        
        Args:
            model_name: Name of pre-trained model from transformers library
        """
        self.model_name = model_name
        self._initialize_model()
        
    def _initialize_model(self):
        """Load model and tokenizer from transformers"""
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
    
    def score(self, prompt: str, completion: str) -> float:
        """
        Score a LLM completion for uncertainty (0=high uncertainty, 1=low uncertainty)
        
        Args:
            prompt: Input prompt given to LLM
            completion: Generated output from LLM
            
        Returns:
            Confidence score between 0 and 1
        """
        raise NotImplementedError


class ProbabilityScorer(UQLMScorer):
    """Scorer based on the average token probability of the completion"""
    
    def score(self, prompt: str, completion: str) -> float:
        """
        Calculate average token probability as confidence score
        
        Args:
            prompt: Input prompt 
            completion: Generated text
            
        Returns:
            Average probability of all tokens in completion (0-1)
        """
        full_text = prompt + completion
        inputs = self.tokenizer(full_text, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            
        # Shift input and logits to align for token probabilities
        input_ids = inputs["input_ids"][:, 1:]
        logits = logits[:, :-1, :]
        
        # Get probabilities for tokens that were actually generated
        probs = softmax(logits, dim=-1)
        token_probs = probs.gather(-1, input_ids.unsqueeze(-1)).squeeze(-1)
        
        # Return average token probability
        return token_probs.mean().item()


class SemanticEntropyScorer(UQLMScorer):
    """Scorer based on semantic similarity between multiple completions"""
    
    def score(self, prompt: str, completion: str, n_samples: int = 5) -> float:
        """
        Calculate semantic entropy score by comparing multiple completions
        
        Args:
            prompt: Input prompt
            completion: Reference completion
            n_samples: Number of samples to generate
            
        Returns:
            Semantic entropy score (higher values = more uncertainty)
        """
        from sentence_transformers import SentenceTransformer
        encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Generate multiple completions
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = []
        
        for _ in range(n_samples):
            generated = self.model.generate(
                **inputs,
                max_new_tokens=len(self.tokenizer(completion)["input_ids"]),
                do_sample=True
            )
            outputs.append(self.tokenizer.decode(generated[0], skip_special_tokens=True))
            
        # Encode all completions and reference
        embeddings = encoder.encode([completion] + outputs)