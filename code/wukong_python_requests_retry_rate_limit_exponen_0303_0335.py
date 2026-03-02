#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Requests HTTP Library Demo Script

Learning Source: GitHub psf/requests repository README (https://github.com/psf/requests)
Date: [自动生成当前日期]
Description: Demonstrates core features of Requests HTTP library including:
             - GET/POST requests
             - Authentication
             - Session handling
             - JSON handling
             - Error handling
             - Connection pooling
"""

import requests
from requests.exceptions import RequestException

def main():
    # Example 1: Basic GET request with authentication
    try:
        print("=== Example 1: Basic GET with Authentication ===")
        # Make authenticated GET request to httpbin
        response = requests.get(
            'https://httpbin.org/basic-auth/user/pass',
            auth=('user', 'pass')  # Basic auth credentials
        )
        
        # Check if request was successful (status code 200)
        response.raise_for_status()
        
        # Print response details
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers['content-type']}")
        print(f"Encoding: {response.encoding}")
        print("Response JSON:", response.json())
        
    except RequestException as e:
        print(f"Request failed: {e}")

    # Example 2: Session with persistent cookies and connection pooling
    try:
        print("\n=== Example 2: Session Persistence ===")
        # Create session for connection reuse
        with requests.Session() as session:
            # First request sets cookie
            resp1 = session.get('https://httpbin.org/cookies/set/sessioncookie/123456789')
            print("First request cookies:", resp1.json()['cookies'])
            
            # Subsequent requests maintain cookies
            resp2 = session.get('https://httpbin.org/cookies')
            print("Second request cookies:", resp2.json()['cookies'])
            
    except RequestException as e:
        print(f"Session request failed: {e}")

    # Example 3: POST JSON data
    try:
        print("\n=== Example 3: POST JSON Data ===")
        # Sample JSON payload
        payload = {
            'title': 'Requests Demo',
            'body': 'Demonstrating POST with JSON',
            'userId': 1
        }
        
        # POST request with JSON payload
        response = requests.post(
            'https://httpbin.org/post',
            json=payload  # Automatically sets Content-Type to application/json
        )
        
        # Print formatted response
        print("Server received:", response.json()['json'])
        
    except RequestException as e:
        print(f"POST request failed: {e}")

    # Example 4: Error handling and timeouts
    try:
        print("\n=== Example 4: Error Handling ===")
        # Request with short timeout (will likely fail)
        response = requests.get(
            'https://httpbin.org/delay/5',  # Server waits 5 seconds to respond
            timeout=1  # Timeout after 1 second
        )
    except requests.Timeout:
        print("Request timed out (as expected)")
    except RequestException as e:
        print(f"Request error: {e}")
    else:
        print("Unexpected success!")

if __name__ == '__main__':
    main()