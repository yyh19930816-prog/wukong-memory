#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Celery Task Queue Demo
Based on celery/celery GitHub repository README (https://github.com/celery/celery)
Created: 2023-11-20
Description: Demonstrates core Celery functionality for asynchronous task processing
using RabbitMQ as the broker and Redis as the result backend.
"""

from celery import Celery
import time

# Define Celery application with Redis backend
# Broker URL points to RabbitMQ server (default port)
# Backend URL points to Redis server for storing task results
app = Celery(
    'tasks',
    broker='amqp://guest:guest@localhost:5672//',
    backend='redis://localhost:6379/0',
)

# Basic configuration settings
app.conf.update(
    task_serializer='json',  # Use JSON for serialization
    accept_content=['json'],  # Only accept JSON content
    result_serializer='json',  # Store results as JSON
    timezone='UTC',  # Use UTC timezone
    enable_utc=True,  # Enable UTC time
)

# Simple task that simulates long-running operation
@app.task
def add(x, y):
    """Add two numbers after simulating processing time."""
    print(f"Starting addition task: {x} + {y}")
    time.sleep(2)  # Simulate processing time
    result = x + y
    print(f"Task completed: {result}")
    return result

# Task that processes strings with retry mechanism
@app.task(bind=True, max_retries=3)
def process_string(self, text):
    """Process string input with retry mechanism."""
    try:
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
            
        print(f"Processing string: {text}")
        time.sleep(1)  # Simulate processing time
        return text.upper()
    except ValueError as exc:
        print(f"Retrying task: {exc}")
        self.retry(exc=exc, countdown=2)  # Retry after 2 seconds

if __name__ == '__main__':
    print("Celery task demonstration")
    print("Running sample tasks (this may take a few seconds)...")
    
    # Example 1: Simple addition task
    result = add.delay(4, 6)  # Send task to Celery worker
    print(f"Task ID (add): {result.id}")
    
    # Example 2: String processing task
    string_task = process_string.delay("hello celery")
    print(f"Task ID (process_string): {string_task.id}")
    
    # Wait for results (in real apps you wouldn't block like this)
    print("\nWaiting for task results...")
    print(f"Addition result: {result.get(timeout=10)}")
    print(f"String result: {string_task.get(timeout=10)}")