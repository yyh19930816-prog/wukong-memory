#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAGFlow Python Implementation
Based on infiniflow/ragflow GitHub repository README (https://github.com/infiniflow/ragflow)
Created: 2023-11-15
Description: A simplified implementation of RAGFlow's core functionality - Retrieval Augmented Generation pipeline.
"""

from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline

class RAGFlow:
    """
    Simplified RAG (Retrieval Augmented Generation) pipeline implementation.
    Combines retrieval from document database with LLM generation.
    """
    
    def __init__(self, retriever_model: str = "all-MiniLM-L6-v2", 
                 generator_model: str = "gpt2"):
        """
        Initialize RAG pipeline with retriever and generator models.
        
        Args:
            retriever_model: Name of sentence transformer model for retrieval
            generator_model: Name of LLM for text generation
        """
        self.retriever = SentenceTransformer(retriever_model)
        self.generator = pipeline("text-generation", model=generator_model)
        self.documents = []  # Store document texts
        self.embeddings = None  # Store document embeddings
        
    def add_documents(self, documents: List[str]):
        """
        Add documents to the retriever database and compute embeddings.
        
        Args:
            documents: List of document texts to add
        """
        self.documents.extend(documents)
        new_embeddings = self.retriever.encode(documents)
        
        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve most relevant documents for a query.
        
        Args:
            query: Input query/text to find relevant documents for
            top_k: Number of top documents to return
            
        Returns:
            List of dicts containing document text and similarity score
        """
        if not self.documents:
            return []
            
        query_embedding = self.retriever.encode(query).reshape(1, -1)
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [
            {"text": self.documents[i], "score": similarities[i]} 
            for i in top_indices
        ]
    
    def generate(self, prompt: str, retrieved_texts: List[str], 
                 max_length: int = 50) -> str:
        """
        Generate text combining prompt and retrieved information.
        
        Args:
            prompt: Input prompt/question
            retrieved_texts: List of relevant texts from retrieval step
            max_length: Maximum length of generated text
            
        Returns:
            Generated text combining prompt and retrieved information
        """
        context = "\n".join(retrieved_texts[:2])  # Use top 2 retrieved texts
        full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}\nAnswer:"
        
        generated = self.generator(
            full_prompt, 
            max_length=max_length, 
            num_return_sequences=1,
            truncation=True
        )
        
        return generated[0]['generated_text']
    
    def query(self, question: str, top_k: int = 3) -> str: