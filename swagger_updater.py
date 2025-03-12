#!/usr/bin/env python
import json
import argparse
import os
import sys

def load_json_file(file_path):
    """Load JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None

def save_json_file(file_path, data):
    """Save JSON to file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved updated schema to {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving {file_path}: {str(e)}")
        return False

def normalize_path(path):
    """Normalize API path for comparison"""
    # Remove trailing slash for comparison
    if path.endswith('/') and len(path) > 1:
        path = path[:-1]
        
    # Remove /api prefix if present
    if path.startswith('/api'):
        path = path[4:]
    
    # Replace numeric parts with {id}
    parts = path.split('/')
    normalized = []
    for part in parts:
        if part and part.isdigit():
            normalized.append('{id}')
        else:
            normalized.append(part)
    
    normalized_path = '/'.join(normalized)
    
    # Ensure path starts with /
    if not normalized_path.startswith('/'):
        normalized_path = '/' + normalized_path
        
    return normalized_path

def suggest_path_updates(test_results, swagger_schema):
    """Suggest updates to Swagger schema based on test results"""
    print("\n🔍 Analyzing test results vs Swagger schema...")
    
    # Extract tested endpoints
    tested_endpoints = {}
    for result in test_results.get("details", []):
        if result.get("passed", False):
            norm_path = normalize_path(result["endpoint"])
            key = (norm_path, result["method"].lower())
            tested_endpoints[key] = result
            print(f"Tested endpoint: {result['method']} {result['endpoint']} -> normalized: {norm_path}")
    
    # Extract documented endpoints
    documented_endpoints = set()
    for path, methods in swagger_schema.get('paths', {}).items():
        for method in methods.keys():
            norm_path = normalize_path(path)
            documented_endpoints.add((norm_path, method.lower()))
            print(f"Documented endpoint: {method.upper()} {path} -> normalized: {norm_path}")
    
    # Find missing endpoints
    missing_endpoints = []
    for key, result in tested_endpoints.items():
        if key not in documented_endpoints:
            # Skip auth endpoints as they might be in security definitions
            if '/auth/' in key[0]:
                continue
            missing_endpoints.append((key[0], key[1], result))
    
    if not missing_endpoints:
        print("✅ All tested endpoints are documented in the Swagger schema!")
        return swagger_schema, False
    
    print(f"⚠️ Found {len(missing_endpoints)} endpoints tested but not documented:")
    
    # Update schema with missing endpoints
    updated_schema = swagger_schema.copy()
    
    for path, method, result in missing_endpoints:
        print(f"  - {method.upper()} {path}")
        
        # Convert normalized path back to Swagger format
        swagger_path = path
        if not swagger_path.startswith('/'):
            swagger_path = '/' + swagger_path
        
        # Add path if it doesn't exist
        if swagger_path not in updated_schema['paths']:
            updated_schema['paths'][swagger_path] = {}
        
        # Add method to path
        if method not in updated_schema['paths'][swagger_path]:
            # Generate operation ID
            operation_id = generate_operation_id(swagger_path, method)
            
            # Create basic method definition
            method_def = {
                "operationId": operation_id,
                "description": f"Auto-generated from API tests",
                "responses": {}
            }
            
            # Add parameters if any
            parameters = []
            for part in swagger_path.split('/'):
                if part.startswith('{') and part.endswith('}'):
                    param_name = part[1:-1]
                    parameters.append({
                        "name": param_name,
                        "in": "path",
                        "required": True,
                        "type": "integer",
                        "description": f"ID of the {param_name}"
                    })
            
            if parameters:
                method_def["parameters"] = parameters
            
            # Add request body parameter for POST/PUT/PATCH
            if method in ["post", "put", "patch"]:
                body_param = {
                    "name": "body",
                    "in": "body",
                    "required": True,
                    "schema": {
                        "type": "object"
                    }
                }
                
                # Try to extract schema from test results
                if "response_data" in result:
                    try:
                        # For POST, assume request is similar to response
                        schema = extract_schema_from_json(result["response_data"])
                        if schema:
                            body_param["schema"] = schema
                    except:
                        pass
                
                if not parameters:
                    method_def["parameters"] = []
                method_def["parameters"].append(body_param)
            
            # Add expected responses
            status_code = str(result.get("status_code", 200))
            response_def = {
                "description": get_status_description(status_code)
            }
            
            # Add response schema if available
            if "response_data" in result:
                try:
                    schema = extract_schema_from_json(result["response_data"])
                    if schema:
                        response_def["schema"] = schema
                except:
                    pass
            
            method_def["responses"][status_code] = response_def
            
            # Add common error responses
            for code, desc in [("400", "Bad Request"), ("401", "Unauthorized"), ("404", "Not Found")]:
                if code != status_code:  # Avoid duplicating the success code
                    method_def["responses"][code] = {"description": desc}
            
            updated_schema['paths'][swagger_path][method] = method_def
    
    return updated_schema, True

def extract_schema_from_json(data):
    """Extract schema definition from JSON data"""
    if isinstance(data, dict):
        properties = {}
        for key, value in data.items():
            if isinstance(value, dict):
                properties[key] = extract_schema_from_json(value)
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    properties[key] = {
                        "type": "array",
                        "items": extract_schema_from_json(value[0])
                    }
                else:
                    properties[key] = {
                        "type": "array",
                        "items": {"type": get_json_type(value[0]) if value else "string"}
                    }
            else:
                properties[key] = {"type": get_json_type(value)}
        
        return {
            "type": "object",
            "properties": properties
        }
    elif isinstance(data, list):
        if data and isinstance(data[0], dict):
            return {
                "type": "array",
                "items": extract_schema_from_json(data[0])
            }
        else:
            return {
                "type": "array",
                "items": {"type": get_json_type(data[0]) if data else "string"}
            }
    else:
        return {"type": get_json_type(data)}

def get_json_type(value):
    """Convert Python type to JSON Schema type"""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "number"
    elif isinstance(value, str):
        return "string"
    else:
        return "string"  # Default to string for unknown types

def get_status_description(status_code):
    """Get description for HTTP status code"""
    descriptions = {
        "200": "OK",
        "201": "Created",
        "204": "No Content",
        "400": "Bad Request",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "Not Found",
        "500": "Internal Server Error"
    }
    return descriptions.get(status_code, "Unknown Status")

def generate_operation_id(path, method):
    """Generate operation ID from path and method"""
    # Remove leading/trailing slashes and split
    clean_path = path.strip('/')
    parts = clean_path.split('/')
    
    # Remove IDs and parameter placeholders
    clean_parts = []
    for part in parts:
        if not (part.isdigit() or (part.startswith('{') and part.endswith('}'))) and part:
            clean_parts.append(part)
    
    # Generate appropriate prefix
    prefixes = {
        "get": "get",
        "post": "create",
        "put": "update",
        "patch": "partial_update", 
        "delete": "delete"
    }
    prefix = prefixes.get(method, method)
    
    # Handle special cases
    if method == "get":
        # For detail view (if ID in path)
        if any(part.isdigit() or (part.startswith('{') and part.endswith('}')) for part in parts):
            if len(clean_parts) > 0:
                return f"get_{clean_parts[-1]}_detail"
        else:
            # For list view
            if len(clean_parts) > 0:
                return f"get_{clean_parts[-1]}_list"
    
    # For nested resources
    if len(clean_parts) > 1:
        if method == "post":
            return f"create_{clean_parts[-1]}_for_{clean_parts[0]}"
        elif method == "get":
            return f"get_{clean_parts[-1]}_for_{clean_parts[0]}"
    
    # Default case
    resource = "_".join(clean_parts)
    return f"{prefix}_{resource}"

def main():
    parser = argparse.ArgumentParser(description='Update Swagger schema based on API test results')
    parser.add_argument('--test-results', '-r', type=str, required=True, 
                        help='Path to test results JSON file')
    parser.add_argument('--input-schema', '-s', type=str, required=True,
                        help='Path to Swagger schema JSON file')
    parser.add_argument('--output-schema', '-o', type=str, default=None,
                        help='Path for the updated schema (defaults to overwrite input schema)')
    
    args = parser.parse_args()
    
    # Check if files exist
    if not os.path.exists(args.test_results):
        print(f"❌ Test results file not found: {args.test_results}")
        sys.exit(1)
    
    if not os.path.exists(args.input_schema):
        print(f"❌ Swagger schema file not found: {args.input_schema}")
        sys.exit(1)
    
    # Load files
    test_results = load_json_file(args.test_results)
    swagger_schema = load_json_file(args.input_schema)
    
    if not test_results or not swagger_schema:
        sys.exit(1)
    
    # Suggest updates
    updated_schema, changed = suggest_path_updates(test_results, swagger_schema)
    
    # Save updated schema if changed
    if changed:
        output_path = args.output_schema if args.output_schema else args.input_schema
        save_json_file(output_path, updated_schema)
        print("✅ Schema updated with missing endpoints")
    else:
        print("✅ No changes needed to schema")

if __name__ == "__main__":
    main() 