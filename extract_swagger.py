import requests
import json
import sys

def extract_swagger_schema(base_url):
    """
    Extract Swagger schema from the API
    """
    try:
        # Try standard schema endpoints
        schema_endpoints = [
            '/api/schema/',
            '/api/openapi.json',
            '/api/swagger.json',
            '/api/schema.json',
            '/openapi.json',
            '/swagger.json'
        ]
        
        for endpoint in schema_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}")
                if response.status_code == 200:
                    schema = response.json()
                    with open('api_schema.json', 'w') as f:
                        json.dump(schema, f, indent=2)
                    print(f"✅ Successfully extracted schema from {base_url}{endpoint}")
                    return True
            except Exception as e:
                pass
        
        print("❌ Failed to extract schema from standard endpoints.")
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    base_url = "http://localhost:8050"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    success = extract_swagger_schema(base_url)
    if not success:
        print("Could not extract schema. Tests will run without schema validation.") 