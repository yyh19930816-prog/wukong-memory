#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAGFlow Python Implementation
Source: https://github.com/infiniflow/ragflow
Date: May 2024
Description: A simplified Python implementation of RAGFlow's core retrieval-augmented generation functionality.
"""

import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline

class RagFlow:
    """
    Simplified RAGFlow implementation with document retrieval and generation capabilities.
    """
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize with embedding model and generator model.
        
        Args:
            model_name: Name of the SentenceTransformer model for embeddings
        """
        # Initialize embedding model (sentence transformer)
        self.embedding_model = SentenceTransformer(model_name)
        
        # Initialize QA model (HF pipeline)
        self.qa_model = pipeline(
            "question-answering", 
            model="deepset/roberta-base-squad2"
        )
        
        # Document store (in-memory dictionary)
        self.doc_store = {}
        self.doc_embeddings = None
    
    def index_documents(self, documents):
        """
        Index documents by generating embeddings and storing them.
        
        Args:
            documents: List of documents (strings) to index
        """
        # Generate embeddings for all documents
        embeddings = self.embedding_model.encode(documents)
        
        # Store documents and their embeddings
        self.doc_store = {f"doc_{i}": doc for i, doc in enumerate(documents)}
        self.doc_embeddings = embeddings
    
    def retrieve_documents(self, query, top_k=3):
        """
        Retrieve most relevant documents based on query.
        
        Args:
            query: Search query string
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        if not self.doc_store:
            raise ValueError("No documents indexed yet")
            
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Calculate similarity scores
        scores = np.dot(self.doc_embeddings, query_embedding)
        
        # Get top-k document indices
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        # Return documents
        return [self.doc_store[f"doc_{i}"] for i in top_indices]
    
    def generate_answer(self, question, context=None, retrieve_first=True):
        """
        Generate answer to question using RAG approach.
        
        Args:
            question: Question to answer
            context: Optional context (if not provided, will retrieve)
            retrieve_first: Whether to retrieve context first
            
        Returns:
            Dictionary with answer and context
        """
        if retrieve_first or not context:
            # Retrieve relevant documents as context
            context = " ".join(self.retrieve_documents(question))
        
        # Generate answer using QA model
        result = self.qa_model({
            "question": question,
            "context": context
        })
        
        return {
            "answer": result["answer"],
            "score": result["score"],
            "context": context
        }

# Example usage
if __name__ == "__main__":
    # Sample documents
    documents = [
        "RAGFlow is an open-source RAG (Retrieval-Augmented Generation) engine.",
        "It provides semantic retrieval and LLM generation capabilities.",
        "RAGFlow supports multiple document formats including PDF, Word and Excel.",
        "You can deploy RAGFlow locally or use their cloud demo."
    ]
    
    # Initialize RAGFlow
    rag = RagFlow()
    
    # Index documents
    print("