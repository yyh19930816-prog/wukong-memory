#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Celery Demo Task Queue Implementation
Source: https://github.com/celery/celery/blob/main/README.rst
Date: 2023-11-15
Description: Minimal Celery task queue example with Redis broker and result backend.
Demonstrates async task execution and result retrieval.
"""

from celery import Celery
import time

# Initialize Celery app with Redis as both broker and result backend
app = Celery(
    'demo_tasks',
    broker='redis://localhost:6379/0',  # Message broker URL
    backend='redis://localhost:6379/1'  # Result backend URL
)

@app.task
def add(x, y):
    """Simple addition task with delay to simulate processing."""
    time.sleep(2)  # Simulate long-running task
    return x + y

@app.task
def multiply(x, y):
    """Multiplication task demonstrating chaining."""
    time.sleep(1)  # Simulate processing time
    return x * y

def main():
    """Demonstrate Celery task execution patterns."""
    print("Celery Demo - Asynchronous Task Processing")
    
    # Execute tasks asynchronously
    add_result = add.delay(4, 6)
    mul_result = multiply.delay(5, 3)
    
    print("Tasks submitted. Waiting for results...")
    
    # Check task status (not ready immediately)
    print(f"Add task ready: {add_result.ready()}")
    print(f"Multiply task ready: {mul_result.ready()}")
    
    # Wait and get results
    try:
        print(f"Add result (after 2s wait): {add_result.get(timeout=3)}")
        print(f"Multiply result (after 2s wait): {mul_result.get(timeout=3)}")
    except Exception as e:
        print(f"Error getting results: {e}")
    
    # Demonstrate task chain
    print("\nDemonstrating task chaining:")
    chain_result = (add.s(2, 3) | multiply.s(4))().get()  # (2 + 3) * 4
    print(f"Chained task result: {chain_result}")

if __name__ == '__main__':
    main()