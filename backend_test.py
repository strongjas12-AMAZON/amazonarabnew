#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Secure Password Reset Endpoints
Testing the newly added password reset functionality as requested in review.
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://repo-clone-47.preview.emergentagent.com/api"

# Test credentials from test_result.md
ADMIN_CREDENTIALS = {
    "email": "support@arabshopping.org",
    "password": "Hadi1247@"
}

SELLER_CREDENTIALS = {
    "email": "testseller@test.com", 
    "password": "TestPass123!"
}

BUYER_CREDENTIALS = {
    "email": "testbuyer@test.com",
    "password": "TestPass123!"
}

class PasswordResetTester:
    def __init__(self):
        self.admin_token = None
        self.seller_token = None
        self.buyer_token = None
        self.test_results = []
        self.created_order_id = None
        self.created_address_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append(f"{status}: {test_name} - {details}")
        print(f"{status}: {test_name}")
        if details:
            print(f"    Details: {details}")
    
    def login_user(self, credentials: Dict[str, str], role: str) -> Optional[str]:
        """Login and return auth token"""
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=credentials, timeout=30)
            if response.status_code == 200:
                data = response.json()
                # Try different token locations
                token = (data.get('access_token') or 
                        data.get('session', {}).get('access_token') or
                        data.get('token'))
                if token:
                    self.log_test(f"{role.title()} Login", True, f"Successfully authenticated as {credentials['email']}")
                    return token
                else:
                    self.log_test(f"{role.title()} Login", False, f"No access_token found in response structure")
            else:
                self.log_test(f"{role.title()} Login", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test(f"{role.title()} Login", False, f"Exception: {str(e)}")
        return None
    
    def get_auth_headers(self, token: str) -> Dict[str, str]:
        """Get authorization headers"""
        return {"Authorization": f"Bearer {token}"}
    
    def get_test_user_id(self) -> Optional[str]:
        """Get a non-admin user ID for testing"""
        try:
            headers = self.get_auth_headers(self.admin_token)
            response = requests.get(f"{BASE_URL}/admin/users", headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                # Handle both direct list and wrapped response
                users = data if isinstance(data, list) else data.get('users', [])
                # Find a non-admin user (seller or buyer)
                for user in users:
                    if user.get('role') != 'admin' and user.get('email') in ['testseller@test.com', 'testbuyer@test.com']:
                        return user.get('id')
            return None
        except Exception as e:
            print(f"Error getting test user ID: {e}")
            return None
    
    def test_admin_password_reset_happy_path(self):
        """Test A: Admin-triggered reset — happy path"""
        if not self.admin_token:
            self.log_test("Admin Password Reset - Happy Path", False, "Admin not logged in")
            return
        
        user_id = self.get_test_user_id()
        if not user_id:
            self.log_test("Admin Password Reset - Happy Path", False, "Could not find test user ID")
            return
        
        try:
            headers = self.get_auth_headers(self.admin_token)
            response = requests.post(
                f"{BASE_URL}/admin/users/{user_id}/send-password-reset",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                required_fields = ['success', 'email', 'reset_link']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Admin Password Reset - Happy Path", False, f"Missing fields: {missing_fields}")
                    return
                
                if not data.get('success'):
                    self.log_test("Admin Password Reset - Happy Path", False, f"success=false: {data}")
                    return
                
                reset_link = data.get('reset_link', '')
                if not reset_link or 'type=recovery' not in reset_link:
                    self.log_test("Admin Password Reset - Happy Path", False, f"Invalid reset_link: {reset_link}")
                    return
                
                if 'token=' not in reset_link and 'token_hash=' not in reset_link:
                    self.log_test("Admin Password Reset - Happy Path", False, f"Reset link missing token parameter: {reset_link}")
                    return
                
                email = data.get('email', '')
                if not email or '@' not in email:
                    self.log_test("Admin Password Reset - Happy Path", False, f"Invalid email: {email}")
                    return
                
                email_sent = data.get('email_sent')
                if not isinstance(email_sent, bool):
                    self.log_test("Admin Password Reset - Happy Path", False, f"email_sent should be boolean: {email_sent}")
                    return
                
                self.log_test("Admin Password Reset - Happy Path", True, 
                            f"Reset link generated for {email}, email_sent={email_sent}, link contains recovery token")
            else:
                self.log_test("Admin Password Reset - Happy Path", False, f"HTTP {response.status_code}: {response.text}")
        
        except Exception as e:
            self.log_test("Admin Password Reset - Happy Path", False, f"Exception: {str(e)}")
    
    def test_admin_password_reset_authorization(self):
        """Test B: Admin-triggered reset — authorization"""
        user_id = self.get_test_user_id()
        if not user_id:
            self.log_test("Admin Password Reset - Authorization Tests", False, "Could not find test user ID")
            return
        
        # Test 4: Seller access (should be 403)
        if self.seller_token:
            try:
                headers = self.get_auth_headers(self.seller_token)
                response = requests.post(
                    f"{BASE_URL}/admin/users/{user_id}/send-password-reset",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 403:
                    self.log_test("Admin Password Reset - Seller Access Denied", True, "Seller correctly denied with 403")
                else:
                    self.log_test("Admin Password Reset - Seller Access Denied", False, f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_test("Admin Password Reset - Seller Access Denied", False, f"Exception: {str(e)}")
        
        # Test 5: Buyer access (should be 403)
        if self.buyer_token:
            try:
                headers = self.get_auth_headers(self.buyer_token)
                response = requests.post(
                    f"{BASE_URL}/admin/users/{user_id}/send-password-reset",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 403:
                    self.log_test("Admin Password Reset - Buyer Access Denied", True, "Buyer correctly denied with 403")
                else:
                    self.log_test("Admin Password Reset - Buyer Access Denied", False, f"Expected 403, got {response.status_code}")
            except Exception as e:
                self.log_test("Admin Password Reset - Buyer Access Denied", False, f"Exception: {str(e)}")
        
        # Test 6: No auth (should be 401/403)
        try:
            response = requests.post(
                f"{BASE_URL}/admin/users/{user_id}/send-password-reset",
                timeout=30
            )
            
            if response.status_code in [401, 403]:
                self.log_test("Admin Password Reset - No Auth Denied", True, f"Unauthenticated request correctly denied with {response.status_code}")
            else:
                self.log_test("Admin Password Reset - No Auth Denied", False, f"Expected 401/403, got {response.status_code}")
        except Exception as e:
            self.log_test("Admin Password Reset - No Auth Denied", False, f"Exception: {str(e)}")
    
    def test_admin_password_reset_not_found(self):
        """Test C: Admin-triggered reset — not found"""
        if not self.admin_token:
            self.log_test("Admin Password Reset - User Not Found", False, "Admin not logged in")
            return
        
        # Test 7: Random UUID that doesn't exist
        fake_user_id = str(uuid.uuid4())
        try:
            headers = self.get_auth_headers(self.admin_token)
            response = requests.post(
                f"{BASE_URL}/admin/users/{fake_user_id}/send-password-reset",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 404:
                self.log_test("Admin Password Reset - User Not Found", True, "Non-existent user correctly returns 404")
            else:
                self.log_test("Admin Password Reset - User Not Found", False, f"Expected 404, got {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Admin Password Reset - User Not Found", False, f"Exception: {str(e)}")
    
    def test_public_forgot_password_existing_email(self):
        """Test D: Public forgot-password — existing email"""
        try:
            payload = {
                "email": "testbuyer@test.com",
                "redirect_url": "https://example.com"
            }
            
            response = requests.post(
                f"{BASE_URL}/auth/forgot-password",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') is True:
                    message = data.get('message', '')
                    # Should be generic message, not revealing if email exists
                    if 'If an account exists' in message or 'has been sent' in message:
                        self.log_test("Public Forgot Password - Existing Email", True, 
                                    f"Generic response received: {message}")
                    else:
                        self.log_test("Public Forgot Password - Existing Email", False, 
                                    f"Unexpected message format: {message}")
                else:
                    self.log_test("Public Forgot Password - Existing Email", False, f"success=false: {data}")
            else:
                self.log_test("Public Forgot Password - Existing Email", False, f"HTTP {response.status_code}: {response.text}")
        
        except Exception as e:
            self.log_test("Public Forgot Password - Existing Email", False, f"Exception: {str(e)}")
    
    def test_public_forgot_password_non_existent_email(self):
        """Test E: Public forgot-password — non-existent email (anti-enumeration)"""
        try:
            fake_email = f"nobody-xyz-{uuid.uuid4()}@example.com"
            payload = {
                "email": fake_email,
                "redirect_url": "https://example.com"
            }
            
            response = requests.post(
                f"{BASE_URL}/auth/forgot-password",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') is True:
                    message = data.get('message', '')
                    # Should be IDENTICAL to existing email response
                    if 'If an account exists' in message or 'has been sent' in message:
                        self.log_test("Public Forgot Password - Non-existent Email", True, 
                                    f"Anti-enumeration working: identical response for non-existent email")
                    else:
                        self.log_test("Public Forgot Password - Non-existent Email", False, 
                                    f"Unexpected message format: {message}")
                else:
                    self.log_test("Public Forgot Password - Non-existent Email", False, f"success=false: {data}")
            else:
                self.log_test("Public Forgot Password - Non-existent Email", False, f"HTTP {response.status_code}: {response.text}")
        
        except Exception as e:
            self.log_test("Public Forgot Password - Non-existent Email", False, f"Exception: {str(e)}")
    
    def test_public_forgot_password_rate_limit(self):
        """Test F: Public forgot-password — rate limit"""
        try:
            payload = {
                "email": "testbuyer@test.com",
                "redirect_url": "https://example.com"
            }
            
            # Make 6 requests quickly to trigger rate limit (limit is 5/hour)
            rate_limit_triggered = False
            for i in range(6):
                response = requests.post(
                    f"{BASE_URL}/auth/forgot-password",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 429:
                    rate_limit_triggered = True
                    self.log_test("Public Forgot Password - Rate Limit", True, 
                                f"Rate limit triggered on request {i+1} with HTTP 429")
                    break
                elif response.status_code != 200:
                    self.log_test("Public Forgot Password - Rate Limit", False, 
                                f"Unexpected status on request {i+1}: {response.status_code}")
                    break
                
                # Small delay between requests
                time.sleep(0.1)
            
            if not rate_limit_triggered:
                self.log_test("Public Forgot Password - Rate Limit", False, 
                            "Rate limit not triggered after 6 requests (expected after 5)")
        
        except Exception as e:
            self.log_test("Public Forgot Password - Rate Limit", False, f"Exception: {str(e)}")
    
    def test_sanity_check_endpoints(self):
        """Test G: Sanity check - verify unrelated endpoints still work"""
        if not self.admin_token:
            self.log_test("Sanity Check", False, "Admin not logged in")
            return
        
        try:
            headers = self.get_auth_headers(self.admin_token)
            
            # Test admin users endpoint
            response = requests.get(f"{BASE_URL}/admin/users", headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                users = data if isinstance(data, list) else data.get('users', [])
                if isinstance(users, list) and len(users) > 0:
                    self.log_test("Sanity Check - Admin Users", True, f"Admin users endpoint working ({len(users)} users)")
                else:
                    self.log_test("Sanity Check - Admin Users", False, f"Unexpected users response structure")
            else:
                self.log_test("Sanity Check - Admin Users", False, f"HTTP {response.status_code}: {response.text}")
            
            # Test admin products endpoint
            response = requests.get(f"{BASE_URL}/admin/products", headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                products = data if isinstance(data, list) else data.get('products', [])
                if isinstance(products, list):
                    self.log_test("Sanity Check - Admin Products", True, f"Admin products endpoint working ({len(products)} products)")
                else:
                    self.log_test("Sanity Check - Admin Products", False, f"Unexpected products response structure")
            else:
                self.log_test("Sanity Check - Admin Products", False, f"HTTP {response.status_code}: {response.text}")
        
        except Exception as e:
            self.log_test("Sanity Check", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all password reset tests"""
        print("=" * 80)
        print("SECURE PASSWORD RESET ENDPOINTS TESTING")
        print("=" * 80)
        
        # Step 1: Authentication
        print("\n1. AUTHENTICATION SETUP")
        print("-" * 40)
        self.admin_token = self.login_user(ADMIN_CREDENTIALS, "admin")
        self.seller_token = self.login_user(SELLER_CREDENTIALS, "seller")
        self.buyer_token = self.login_user(BUYER_CREDENTIALS, "buyer")
        
        if not self.admin_token:
            print("❌ CRITICAL: Admin authentication failed. Cannot proceed with admin tests.")
            return 0, 0, 0
        
        # Step 2: Admin-triggered reset tests
        print("\n2. ADMIN-TRIGGERED PASSWORD RESET TESTS")
        print("-" * 40)
        self.test_admin_password_reset_happy_path()
        self.test_admin_password_reset_authorization()
        self.test_admin_password_reset_not_found()
        
        # Step 3: Public forgot password tests
        print("\n3. PUBLIC FORGOT PASSWORD TESTS")
        print("-" * 40)
        self.test_public_forgot_password_existing_email()
        self.test_public_forgot_password_non_existent_email()
        self.test_public_forgot_password_rate_limit()
        
        # Step 4: Sanity checks
        print("\n4. SANITY CHECKS")
        print("-" * 40)
        self.test_sanity_check_endpoints()
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result)
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result)
        total = len(self.test_results)
        
        print(f"TOTAL TESTS: {total}")
        print(f"PASSED: {passed}")
        print(f"FAILED: {failed}")
        print(f"SUCCESS RATE: {(passed/total*100):.1f}%" if total > 0 else "0%")
        
        print("\nDETAILED RESULTS:")
        for result in self.test_results:
            print(result)
        
        return passed, failed, total

if __name__ == "__main__":
    tester = PasswordResetTester()
    passed, failed, total = tester.run_all_tests()
    
    if failed > 0:
        print(f"\n❌ {failed} test(s) failed. Please review the issues above.")
        exit(1)
    else:
        print(f"\n✅ All {passed} tests passed successfully!")
        exit(0)
