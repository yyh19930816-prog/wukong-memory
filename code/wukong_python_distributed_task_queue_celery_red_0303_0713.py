#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Celery Task Queue Demo
Based on celery/celery README (https://github.com/celery/celery)
Created: 2023-11-20
Description: Demonstrates core Celery functionality including task queuing 
             with Redis broker and result backend, plus task retry mechanism.
"""

from celery import Celery
from celery.exceptions import Retry
import time

# Initialize Celery app with Redis as both broker and result backend
app = Celery(
    'demo_tasks',
    broker='redis://localhost:6379/0',  # Message broker URL
    backend='redis://localhost:6379/1', # Result backend URL
)

# Configuration settings
app.conf.update(
    task_serializer='json',      # JSON serialization for messages
    accept_content=['json'],     # Accept only JSON content
    result_serializer='json',    # JSON serialization for results
    timezone='UTC',              # UTC timezone
    enable_utc=True,             # Enable UTC
    task_track_started=True,     # Track when task starts
    task_default_rate_limit='1/s'# Default rate limit
)

@app.task(bind=True, max_retries=3)  # Bind task to self for retry, max 3 retries
def process_data(self, data):
    """Example task that processes data with retry capability."""
    try:
        print(f"Processing data: {data}")
        # Simulate work
        time.sleep(1)
        
        # Simulate occasional failure (20% chance)
        if int(data) % 5 == 0:
            raise ValueError("Data processing failed!")
            
        return f"Processed: {data}"
    except Exception as exc:
        print(f"Task failed, retrying... ({self.request.retries})")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

@app.task
def add_numbers(a, b):
    """Simple task that adds two numbers."""
    return a + b

if __name__ == '__main__':
    # Demonstrate task queueing (run workers separately)
    print("Queueing demo tasks...")
    
    # Queue simple task
    add_result = add_numbers.delay(5, 3)
    print(f"Queued add_numbers task (id: {add_result.id})")
    
    # Queue tasks with processing
    for i in range(1, 6):
        result = process_data.delay(str(i))
        print(f"Queued process_data task {i} (id: {result.id})")
    
    print("\nRun 'celery -A demo_tasks worker --loglevel=info' to process tasks")