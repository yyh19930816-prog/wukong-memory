#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow Python Implementation 

Based on README from infiniflow/ragflow GitHub repository:
https://github.com/infiniflow/ragflow

Created on: 2023-10-05
Description: A lightweight RAG (Retrieval-Augmented Generation) pipeline implementation
             mimicking core functionalities of RAGFlow including document processing,
             embedding generation, and similarity search.
"""

from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class RagFlow:
    """Main class implementing RAGFlow core functionality"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize RAGFlow with embedding model
        
        Args:
            model_name: Name of SentenceTransformer model to use
        """
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = None
        
    def load_documents(self, docs: List[str]) -> None:
        """
        Load and process documents
        
        Args:
            docs: List of document texts
        """
        print(f"Processing {len(docs)} documents...")
        self.documents = docs
        self.embeddings = self.model.encode(docs)
        print("Documents processing complete.")
        
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Search documents based on query similarity
        
        Args:
            query: Search query text
            top_k: Number of top results to return
            
        Returns:
            List of (document_text, similarity_score) tuples
        """
        if self.embeddings is None:
            raise ValueError("No documents loaded. Call load_documents() first.")
            
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = [(self.documents[i], similarities[i]) for i in top_indices]
        
        return results
    
    def batch_process(self, queries: List[str], top_k: int = 3) -> Dict[str, List[Tuple[str, float]]]:
        """
        Process multiple queries at once
        
        Args:
            queries: List of query texts
            top_k: Number of results per query
            
        Returns:
            Dictionary mapping queries to their search results
        """
        return {query: self.search(query, top_k) for query in queries}


if __name__ == "__main__":
    # Example usage
    print("Initializing RAGFlow...")
    rag = RagFlow()
    
    # Sample documents
    documents = [
        "RAGFlow is an open-source RAG pipeline solution.",
        "It provides document processing and semantic search capabilities.",
        "The project supports multiple languages including English and Chinese.",
        "You can try the online demo at demo.ragflow.io",
    ]
    
    # Load documents
    rag.load_documents(documents)
    
    # Search example
    query = "Where can I try RAGFlow?"
    results = rag.search(query)
    
    print(f"\nSearch results for: '{query}'")
    for doc, score in results:
        print(f"[Score: {score:.3f}] {doc}")