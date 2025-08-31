import requests
import json

# Test customer creation
def test_customer_creation():
    url = "https://web-production-84a3.up.railway.app/api/admin/customers"
    
    # Test data
    customer_data = {
        "name": "Test Customer",
        "email": "test@example.com",
        "phone": "+1234567890",
        "billing_address": "123 Test Street",
        "state": "Test State",
        "pincode": "12345",
        "password": "test123"
    }
    
    print("Testing customer creation...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(customer_data, indent=2)}")
    
    try:
        response = requests.post(url, json=customer_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Expected 401 - Authentication required")
        elif response.status_code == 200:
            print("✅ Customer created successfully!")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_customer_creation()
