#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Requests HTTP Library Example Script
Learning Source: GitHub psf/requests (https://github.com/psf/requests)
Date: [Current Date]
Description: Demonstrates core functionality of Requests library including:
- GET/POST requests
- Authentication
- Session persistence
- JSON handling
- Error handling
"""

import requests

def basic_get_request():
    """Demonstrate basic GET request and response handling"""
    print("\n=== Basic GET Request ===")
    url = "https://httpbin.org/get"
    
    try:
        # Send GET request
        response = requests.get(url)
        
        # Check if request was successful (status code 200)
        if response.status_code == 200:
            print(f"Request successful. Status code: {response.status_code}")
            print(f"Response headers: {response.headers['content-type']}")
            print(f"Response encoding: {response.encoding}")
            print("Sample response data:")
            print(response.json())  # Parse JSON response
        else:
            print(f"Request failed with status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def basic_auth_example():
    """Demonstrate HTTP basic authentication"""
    print("\n=== Basic Authentication ===")
    auth_url = "https://httpbin.org/basic-auth/user/pass"
    
    try:
        # Send GET request with basic auth
        response = requests.get(auth_url, auth=('user', 'pass'))
        
        if response.status_code == 200:
            print("Authentication successful!")
            print(response.json())
        else:
            print(f"Authentication failed. Status code: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"Authentication request failed: {e}")

def session_example():
    """Demonstrate session persistence with cookies"""
    print("\n=== Session Persistence ===")
    login_url = "https://httpbin.org/cookies/set/sessioncookie/123456789"
    check_url = "https://httpbin.org/cookies"
    
    # Create a session object
    with requests.Session() as session:
        try:
            # First request to set cookie
            session.get(login_url)
            
            # Second request will send the cookie
            response = session.get(check_url)
            
            if response.status_code == 200:
                print("Session cookies:")
                print(response.json())
        
        except requests.exceptions.RequestException as e:
            print(f"Session request failed: {e}")

def post_json_example():
    """Demonstrate POST request with JSON payload"""
    print("\n=== POST JSON Data ===")
    post_url = "https://httpbin.org/post"
    payload = {
        "name": "John Doe",
        "age": 30,
        "city": "New York"
    }
    
    try:
        # Send POST request with JSON data
        response = requests.post(post_url, json=payload)
        
        if response.status_code == 200:
            print("POST request successful")
            print("Received data:")
            print(response.json())
    
    except requests.exceptions.RequestException as e:
        print(f"POST request failed: {e}")

def main():
    """Main function to demonstrate all examples"""
    print("Requests Library Demonstration")
    print("============================\n")
    
    # Run all demonstration functions
    basic_get_request()
    basic_auth_example()
    session_example()
    post_json_example()

    print("\nDemonstration complete!")

if __name__ == "__main__":
    main()