import requests
import json

def test_railway_backend():
    base_url = "https://web-production-84a3.up.railway.app"
    
    print("Testing Railway Backend Status...")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"✅ Health Check: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
    
    # Test 2: API test
    try:
        response = requests.get(f"{base_url}/api/test", timeout=10)
        print(f"✅ API Test: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ API Test Failed: {e}")
    
    # Test 3: Auth register endpoint
    try:
        response = requests.post(f"{base_url}/api/auth/register", 
                               json={"test": "data"}, 
                               timeout=10)
        print(f"✅ Auth Register: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Auth Register Failed: {e}")

if __name__ == "__main__":
    test_railway_backend()
