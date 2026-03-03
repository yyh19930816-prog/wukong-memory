#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Celery Task Queue Demo
Learn from: https://github.com/celery/celery
Date: 2023-11-15
Description: A simple Celery demo showing asynchronous task processing with Redis broker.
"""

from celery import Celery
import time

# Initialize Celery app with Redis as broker
# Redis server must be running locally for this to work
app = Celery(
    'demo_tasks',
    broker='redis://localhost:6379/0',  # Redis broker URL
    backend='redis://localhost:6379/0'  # Redis backend for result storage
)

# Configure Celery settings
app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@app.task(bind=True)  # Bind=True gives access to the task instance (self)
def add(self, x, y):
    """Add two numbers together with simulated delay"""
    try:
        # Simulate some processing time
        time.sleep(2)
        result = x + y
        return result
    except Exception as e:
        # Log error if task fails
        self.retry(exc=e, countdown=60)  # Retry after 60 seconds if fails

@app.task
def multiply(x, y):
    """Multiply two numbers together"""
    return x * y

if __name__ == '__main__':
    print("Demo of Celery asynchronous task processing")

    # Send tasks to Celery worker
    add_result = add.delay(4, 4)        # Non-blocking call
    multiply_result = multiply.delay(5, 6)

    print("Tasks submitted to Celery worker. Waiting for results...")

    # Block until task completes (not typical in production)
    try:
        print(f"Add result: {add_result.get(timeout=10)}")
        print(f"Multiply result: {multiply_result.get(timeout=10)}")
    except Exception as e:
        print(f"Error getting results: {str(e)}")

    print("Demo complete. Start Celery worker with:")
    print("celery -A script_name worker --loglevel=info")