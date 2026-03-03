#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Requests HTTP Library Demonstration Script

Learning Source: GitHub psf/requests repository README
Date: [Today's Date]
Description: Demonstrates core features of Requests HTTP library including:
    - GET/POST requests with authentication
    - Response handling (status codes, headers, JSON)
    - Session persistence
    - Error handling
"""

import requests
import json

def main():
    """
    Main function demonstrating Requests library capabilities
    """
    # Example 1: Basic GET request with authentication
    print("\n=== Example 1: Basic GET with Auth ===")
    try:
        response = requests.get(
            'https://httpbin.org/basic-auth/user/pass',
            auth=('user', 'pass')
        )
        
        # Response status and metadata
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Encoding: {response.encoding}")
        
        # Response content handling
        print("\nResponse Text:")
        print(response.text)
        
        print("\nParsed JSON:")
        print(json.dumps(response.json(), indent=2))
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    # Example 2: POST request with JSON payload
    print("\n=== Example 2: POST with JSON ===")
    try:
        payload = {'key1': 'value1', 'key2': 'value2'}
        response = requests.post(
            'https://httpbin.org/post',
            json=payload
        )
        
        print(f"Status Code: {response.status_code}")
        print("\nResponse JSON:")
        print(json.dumps(response.json(), indent=2))
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    # Example 3: Using sessions for persistence
    print("\n=== Example 3: Session Persistence ===")
    try:
        with requests.Session() as session:
            # Set common headers for all session requests
            session.headers.update({'x-test': 'true'})
            
            # First request sets cookies
            session.get('https://httpbin.org/cookies/set/sessioncookie/123')
            
            # Second request maintains cookies and headers
            response = session.get('https://httpbin.org/cookies')
            
            print(f"Status Code: {response.status_code}")
            print("\nCookies:")
            print(json.dumps(response.json(), indent=2))
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    # Example 4: Error handling and timeouts
    print("\n=== Example 4: Error Handling ===")
    try:
        # Intentional timeout with non-existent URL
        response = requests.get(
            'https://httpbin.org/delay/5',
            timeout=0.1
        )
    except requests.exceptions.Timeout:
        print("Timeout occurred (expected)")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == '__main__':
    main()