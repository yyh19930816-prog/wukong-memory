#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAGFlow Python Client Demo
Description: A simplified Python implementation demonstrating RAGFlow's core functionality
             based on the GitHub repository infiniflow/ragflow README
Source: https://github.com/infiniflow/ragflow
Date: 2023-12-01
Features:
    - Document ingestion and processing
    - Vector search capability 
    - API interaction demonstration
    - Basic chat interface simulation
"""

import requests
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class RAGFlowClient:
    """
    A simplified RAGFlow client implementation demonstrating core functionalities:
    - Document processing and embedding
    - Vector similarity search
    - Basic API interactions
    """
    
    def __init__(self):
        # Initialize embedding model (using a lightweight model for demo)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = []
        self.embeddings = None
        
    def ingest_documents(self, documents: List[str]):
        """
        Process and store documents with embeddings
        Args:
            documents: List of text documents to ingest
        """
        print(f"Ingesting {len(documents)} documents...")
        self.documents = documents
        # Generate embeddings for all documents
        self.embeddings = self.embedding_model.encode(documents)
        print("Documents processed successfully!")
        
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Perform semantic search on ingested documents
        Args:
            query: Search query string
            top_k: Number of results to return
        Returns:
            List of results with document text and similarity score
        """
        if not self.embeddings.any():
            raise ValueError("No documents loaded")
            
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(
            [query_embedding],
            self.embeddings
        )[0]
        
        # Get top-k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                "text": self.documents[idx],
                "score": float(similarities[idx])
            })
            
        return results
    
    def query_api(self, question: str) -> str:
        """
        Simulate API call to RAGFlow demo endpoint
        Args:
            question: Query/question to ask
        Returns:
            Simulated API response
        """
        # This is a simulation - real API would use requests.post()
        mock_responses = [
            "Based on the documents, I found relevant information about this topic.",
            "The documentation suggests several approaches to this problem.",
            "I couldn't find definitive information. Could you clarify your question?"
        ]
        return np.random.choice(mock_responses)

def main():
    """Demonstration of RAGFlow core functionality"""
    
    # Initialize client
    client = RAGFlowClient()
    
    # Sample documents (would normally come from files/DB)
    documents = [
        "RAGFlow is an open-source RAG (Retrieval-Augmented Generation) engine.",
        "It combines document retrieval with LLM generation capabilities.",
        "The system supports multiple languages and document formats.",
        "Enterprise features include knowledge base management and API access."
    ]
    
    # Ingest documents
    client.ingest_documents(documents)
    
    # Demo search functionality
    query = "What is R