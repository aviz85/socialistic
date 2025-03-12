#!/usr/bin/env python
import sys
import argparse
from extract_swagger import extract_swagger_schema
from api_tester import ApiTester

def main():
    parser = argparse.ArgumentParser(description='Run API tests against the Socialistic API')
    parser.add_argument('--url', '-u', type=str, default='http://localhost:8050', 
                        help='Base URL of the API (default: http://localhost:8050)')
    parser.add_argument('--schema-path', '-s', type=str, default='api_schema.json',
                        help='Path to save/use Swagger schema (default: api_schema.json)')
    parser.add_argument('--skip-schema-extraction', action='store_true',
                        help='Skip schema extraction and use existing schema file')
    parser.add_argument('--doc-output', '-o', type=str, default='api_test_results.md',
                        help='Path to save documentation validation results (default: api_test_results.md)')
    
    args = parser.parse_args()
    
    print(f"🚀 Starting API tests for {args.url}")
    
    # Extract schema if needed
    if not args.skip_schema_extraction:
        print(f"📃 Extracting Swagger schema from {args.url}")
        extract_swagger_schema(args.url)
    
    # Run API tests
    print(f"🧪 Running API tests...")
    tester = ApiTester(args.url, args.schema_path)
    results = tester.run_all_tests()
    
    # Exit with appropriate status code
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == "__main__":
    main() 