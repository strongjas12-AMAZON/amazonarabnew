#!/usr/bin/env python3
"""
Setup specific test users mentioned in the review request
"""

import requests
import json

BASE_URL = "https://repo-clone-46.preview.emergentagent.com/api"

def create_user_via_register(email, password, name, role, store_name=None):
    """Create user via registration endpoint"""
    try:
        register_data = {
            "email": email,
            "password": password,
            "name": name,
            "role": role
        }
        
        if role == "seller" and store_name:
            register_data["storeName"] = store_name
            
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ Created user: {email} ({role})")
                return True
            else:
                print(f"❌ Failed to create {email}: {data}")
                return False
        else:
            print(f"❌ Failed to create {email}: HTTP {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception creating {email}: {str(e)}")
        return False

def main():
    print("Setting up review test users...")
    
    # Users mentioned in the review request
    users_to_create = [
        {
            "email": "testseller_new@test.com",
            "password": "TestPass123!",
            "name": "Test Seller New",
            "role": "seller",
            "store_name": "Test Seller Store"
        },
        {
            "email": "testbuyer@test.com", 
            "password": "TestPass123!",
            "name": "Test Buyer",
            "role": "buyer"
        }
    ]
    
    for user in users_to_create:
        create_user_via_register(
            user["email"], 
            user["password"], 
            user["name"], 
            user["role"], 
            user.get("store_name")
        )

if __name__ == "__main__":
    main()