#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Learn from: https://github.com/celery/celery (README)
# Date: 2023-11-15
# Description: Basic Celery task queue demo with Redis backend
# Implements core functionality - async task execution with message queue

from celery import Celery
import time

# Initialize Celery with Redis as broker and backend
# Redis server must be running locally or specify connection URL
app = Celery(
    'tasks',  # Module name
    broker='redis://localhost:6379/0',  # Message broker URL
    backend='redis://localhost:6379/1',  # Result backend URL
    broker_connection_retry_on_startup=True  # Required for Celery 5.0+
)

@app.task
def add(x, y):
    """Basic addition task demonstrating synchronous execution"""
    return x + y

@app.task(bind=True)  # bind=True gives access to task instance (self)
def long_running_task(self, duration):
    """Demonstrates long-running task with progress tracking
    
    Args:
        duration (int): How many seconds the task should run
        self: Celery task instance for updating state
    """
    total_steps = 10
    for i in range(total_steps):
        # Update task state with progress info
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': total_steps,
                'percent': (i + 1) / total_steps * 100,
                'status': f'Processing step {i + 1}/{total_steps}'
            }
        )
        time.sleep(duration / total_steps)
    return {'status': 'Completed', 'duration': duration}

if __name__ == '__main__':
    # Demo usage - run this script directly to test tasks
    
    # Simple task (immediate execution without async)
    print("Running simple add task:")
    result = add.delay(4, 6)  # Delay makes it async
    print(f"Task ID: {result.id}. Waiting...")
    print(f"Result: {result.get(timeout=5)}")  # Wait max 5 seconds
    
    # Long-running task with progress tracking
    print("\nRunning long-running task:")
    task = long_running_task.delay(5)  # Run for 5 seconds
    
    while not task.ready():
        # Check task status periodically
        try:
            status = task.result or task.status
            if isinstance(status, dict):
                print(f"\rProgress: {status.get('percent', 0):.0f}% - {status.get('status', '')}", end='')
            else:
                print(f"\rStatus: {task.status}", end='')
            time.sleep(0.5)
        except Exception as e:
            print(f"\nError checking status: {e}")
            break
    
    if task.successful():
        print(f"\nFinal result: {task.result}")