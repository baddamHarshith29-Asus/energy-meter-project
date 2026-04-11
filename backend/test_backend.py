import requests

BASE_URL = "http://localhost:5000/api"

def test_endpoint(endpoint):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"GET {endpoint}: Status {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"GET {endpoint}: Failed - {e}")

def run_tests():
    print("--- Testing Backend Endpoints ---")
    test_endpoint("/health")
    test_endpoint("/branches")
    test_endpoint("/dashboard/1")
    test_endpoint("/predict/1")

if __name__ == "__main__":
    run_tests()
