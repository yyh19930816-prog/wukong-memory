#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow Core Functionality Implementation
Learning Source: https://github.com/infiniflow/ragflow
Date: Current date
Description: A simplified implementation of RAGFlow core functionality - Retrieval Augmented Generation pipeline.
             This script demonstrates document processing, embedding generation and semantic search capabilities.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple

class RAGPipeline:
    """
    Simplified RAGFlow pipeline implementation with core functionality:
    1. Document processing and chunking
    2. Embedding generation
    3. Semantic search and retrieval
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the RAG pipeline with embedding model
        :param model_name: Name of SentenceTransformer model to use
        """
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = None
    
    def add_documents(self, documents: List[str]):
        """
        Add documents to the pipeline and generate embeddings
        :param documents: List of text documents/chunks
        """
        self.documents.extend(documents)
        self._update_embeddings()
        
    def _update_embeddings(self):
        """Generate embeddings for all stored documents"""
        self.embeddings = self.model.encode(self.documents)
    
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Perform semantic search on stored documents
        :param query: Search query string
        :param top_k: Number of top results to return
        :return: List of (document, score) tuples
        """
        query_embedding = self.model.encode([query])
        
        # Calculate cosine similarity between query and documents
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top k most similar documents
        top_indices = similarities.argsort()[-top_k:][::-1]
        return [
            (self.documents[i], float(similarities[i]))
            for i in top_indices
        ]
    
    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve context for RAG pipeline
        :param query: Input query/question
        :param top_k: Number of context passages to retrieve
        :return: Combined context string
        """
        results = self.search(query, top_k)
        return "\n\n".join([doc for doc, score in results])

if __name__ == "__main__":
    # Demo usage of the RAGPipeline
    
    # 1. Initialize pipeline
    rag = RAGPipeline()
    
    # 2. Sample documents (in practice would be loaded from files/database)
    docs = [
        "RAGFlow is an open-source RAG workflow framework.",
        "It provides document processing and semantic search capabilities.",
        "The system uses transformer models for document embeddings.",
        "Retrieval Augmented Generation combines search with language models.",
    ]
    
    # 3. Add documents to pipeline
    rag.add_documents(docs)
    
    # 4. Perform a search query
    query = "What is RAGFlow used for?"
    results = rag.search(query)
    
    print("\nSemantic Search Results:")
    for doc, score in results:
        print(f"\nScore: {score:.3f}\n{doc}")
    
    # 5. Get context for RAG pipeline
    context = rag.retrieve_context(query)