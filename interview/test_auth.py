#!/usr/bin/env python3
"""
Simple test script to verify the authentication system is working.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_root():
    """Test the root endpoint."""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_register():
    """Test user registration."""
    print("Testing user registration...")
    user_data = {"email": "test@example.com", "password": "testpassword123"}
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("Registration successful!")
        print(f"Response: {response.json()}")
    else:
        print(f"Registration failed: {response.text}")
    print()


def test_login():
    """Test user login."""
    print("Testing user login...")
    login_data = {"email": "test@example.com", "password": "testpassword123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Login successful!")
        token_data = response.json()
        print(f"Token: {token_data['access_token'][:50]}...")
        return token_data["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None


def test_protected_endpoint(token):
    """Test a protected endpoint."""
    if not token:
        print("No token available, skipping protected endpoint test.")
        return

    print("Testing protected endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Protected endpoint access successful!")
        print(f"User info: {response.json()}")
    else:
        print(f"Protected endpoint access failed: {response.text}")
    print()


def test_feedback_with_auth(token):
    """Test feedback creation with authentication."""
    if not token:
        print("No token available, skipping feedback test.")
        return

    print("Testing feedback creation with authentication...")
    headers = {"Authorization": f"Bearer {token}"}
    feedback_data = {"text": "This is a test feedback from authenticated user"}
    response = requests.post(
        f"{BASE_URL}/feedback/", json=feedback_data, headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("Feedback creation successful!")
        print(f"Feedback: {response.json()}")
    else:
        print(f"Feedback creation failed: {response.text}")
    print()


def main():
    """Run all tests."""
    print("=== Authentication System Test ===\n")

    try:
        test_root()
        test_register()
        token = test_login()
        test_protected_endpoint(token)
        test_feedback_with_auth(token)

        print("=== Test completed ===")

    except requests.exceptions.ConnectionError:
        print(
            "Error: Could not connect to the server. Make sure the backend is running on http://localhost:8000"
        )
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
