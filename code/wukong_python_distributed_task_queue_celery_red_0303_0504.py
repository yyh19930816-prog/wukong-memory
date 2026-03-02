#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Learning Source: celery/celery GitHub repository README (https://github.com/celery/celery)
# Date: 2023-11-02
# Description: Basic Celery task queue example with Redis broker
# Implements core functionality described in Celery's README - asynchronous task processing
# with Redis as message broker and result backend.

from celery import Celery
import time

# Initialize Celery instance
# Using Redis as both broker (message queue) and result backend
app = Celery(
    'tasks',  # Module name
    broker='redis://localhost:6379/0',  # Redis broker URL
    backend='redis://localhost:6379/0',  # Redis result backend URL
)

# Configure Celery settings
app.conf.update(
    task_serializer='json',  # JSON serialization for tasks
    accept_content=['json'],  # Only accept JSON content
    result_serializer='json',  # JSON serialization for results
    timezone='UTC',  # UTC timezone
    enable_utc=True,  # Enable UTC
)

@app.task(bind=True)  # bind=True gives access to the task instance (self)
def long_running_task(self, x, y):
    """
    Example task that simulates a long-running computation.
    
    Args:
        x: First operand
        y: Second operand
        
    Returns:
        dict: Contains result of computation and task metadata
    """
    try:
        # Simulate work
        time.sleep(2)
        
        result = x * y
        
        # Return task result with metadata
        return {
            'status': 'SUCCESS',
            'result': result,
            'task_id': self.request.id,
        }
    except Exception as e:
        # Handle errors gracefully
        return {
            'status': 'FAILURE',
            'error': str(e),
            'task_id': self.request.id,
        }

def main():
    """
    Main function demonstrating Celery usage.
    """
    print("Starting Celery task demo...")
    
    # Call task asynchronously
    task = long_running_task.delay(4, 5)
    print(f"Task {task.id} submitted to queue")
    
    # Check task status periodically
    while not task.ready():
        print("Waiting for task to complete...")
        time.sleep(0.5)
    
    # Get task result
    result = task.get(timeout=5)
    print(f"Task completed with result: {result}")

if __name__ == '__main__':
    # Run the demo
    main()