import json
import requests
import logging
import sys
from urllib.parse import urljoin
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('api_tester')

class ApiTester:
    def __init__(self, base_url, swagger_path):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.post_id = None
        self.comment_id = None
        self.project_id = None
        self.notification_id = None
        self.test_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
        # Load swagger schema if path is provided
        if swagger_path:
            try:
                with open(swagger_path, 'r') as f:
                    self.swagger = json.load(f)
                logger.info(f"Loaded Swagger schema from {swagger_path}")
            except Exception as e:
                logger.error(f"Error loading Swagger schema: {str(e)}")
                self.swagger = None
        else:
            self.swagger = None
    
    def _track_result(self, endpoint, method, status_code, expected_codes, response=None):
        """Track test result for reporting"""
        result = {
            "endpoint": endpoint,
            "method": method.upper(),
            "status_code": status_code,
            "expected_codes": expected_codes,
            "passed": status_code in expected_codes,
            "time": time.strftime("%H:%M:%S")
        }
        
        # Include response data for documentation
        if response and response.text:
            try:
                result["response_data"] = response.json()
            except:
                result["response_text"] = response.text[:200] if response.text else "Empty response"
        
        # Include error messages for failures
        if not result["passed"] and response:
            try:
                result["error"] = response.json() if response.text else "Empty response"
            except:
                result["error"] = response.text[:200] if response.text else "Empty response"
        
        self.test_results["total"] += 1
        if result["passed"]:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
            
        self.test_results["details"].append(result)
        return result
    
    def report_results(self):
        """Print test results summary"""
        print("\n" + "="*80)
        print(f"API TEST RESULTS - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print(f"Total tests: {self.test_results['total']}")
        print(f"Passed: {self.test_results['passed']}")
        print(f"Failed: {self.test_results['failed']}")
        print(f"Skipped: {self.test_results['skipped']}")
        print("="*80)
        
        if self.test_results["failed"] > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results["details"]:
                if not result["passed"]:
                    print(f"  {result['method']} {result['endpoint']} - Got {result['status_code']}, expected one of {result['expected_codes']}")
                    if "error" in result:
                        print(f"    Error: {result['error']}")
            print("="*80)
        
        # Check doc vs. implementation
        doccheck_result = self.validate_documentation_vs_implementation()
        print(f"\nDocumentation validation: {'PASSED' if doccheck_result['validated'] else 'FAILED'}")
        if not doccheck_result['validated']:
            print("Issues found:")
            for issue in doccheck_result['issues']:
                print(f"  - {issue}")
                
        # Generate documentation update report
        self.generate_documentation_report('api_docs_update.md')
        
        # Save test results as JSON
        self.save_test_results('api_test_results.json')
    
    def save_test_results(self, output_file):
        """Save test results as JSON"""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.test_results, f, indent=2)
            print(f"\nTest results saved to JSON: {output_file}")
        except Exception as e:
            print(f"\nFailed to save test results to {output_file}: {str(e)}")
    
    def generate_documentation_report(self, output_file):
        """Generate a report of required documentation updates"""
        with open(output_file, 'w') as f:
            f.write("# API Documentation Update Report\n\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Total endpoints tested: {self.test_results['total']}\n")
            f.write(f"- Endpoints passed: {self.test_results['passed']}\n")
            f.write(f"- Endpoints failed: {self.test_results['failed']}\n")
            f.write(f"- Endpoints skipped: {self.test_results['skipped']}\n\n")
            
            # Group endpoints by resource
            endpoints_by_resource = {}
            for detail in self.test_results["details"]:
                # Extract resource from endpoint
                parts = detail["endpoint"].split('/')
                resource = None
                for part in parts:
                    if part and not part.isdigit() and part != 'api':
                        resource = part
                        break
                        
                if not resource:
                    resource = "Other"
                    
                if resource not in endpoints_by_resource:
                    endpoints_by_resource[resource] = []
                    
                endpoints_by_resource[resource].append(detail)
            
            # Write endpoints by resource
            f.write("## Endpoints by Resource\n\n")
            for resource, endpoints in sorted(endpoints_by_resource.items()):
                f.write(f"### {resource.title()}\n\n")
                for endpoint in endpoints:
                    status = "✅" if endpoint["passed"] else "❌"
                    f.write(f"- {status} **{endpoint['method']}** `{endpoint['endpoint']}`\n")
                    
                    # Add response details for documentation
                    if "response_data" in endpoint:
                        f.write(f"  - Response Status: {endpoint['status_code']}\n")
                        f.write("  - Response Schema:\n")
                        f.write("```json\n")
                        f.write(json.dumps(endpoint["response_data"], indent=2))
                        f.write("\n```\n")
                f.write("\n")
                
            # Recommendations for documentation updates
            f.write("## Documentation Recommendations\n\n")
            doccheck_result = self.validate_documentation_vs_implementation()
            if doccheck_result['validated']:
                f.write("✅ Documentation is up to date with the tested endpoints.\n\n")
            else:
                f.write("The following updates are recommended for the API documentation:\n\n")
                for issue in doccheck_result['issues']:
                    f.write(f"- {issue}\n")
                    
                # Add templates for missing endpoints
                f.write("\n### Templates for Missing Endpoints\n\n")
                for issue in doccheck_result['issues']:
                    if issue.startswith("Endpoint exists but not documented:"):
                        endpoint_info = issue.replace("Endpoint exists but not documented: ", "").split(" ", 1)
                        if len(endpoint_info) == 2:
                            method, path = endpoint_info
                            f.write(f"#### {method} `{path}`\n\n")
                            f.write("```yaml\n")
                            f.write(f"{path}:\n")
                            f.write(f"  {method.lower()}:\n")
                            f.write(f"    operationId: {self._operation_id_from_path(path, method)}\n")
                            f.write(f"    description: ''\n")
                            
                            # Add parameters section if needed
                            if '{' in path:
                                f.write("    parameters:\n")
                                # Extract path parameters
                                parts = path.split('/')
                                for part in parts:
                                    if part.startswith('{') and part.endswith('}'):
                                        param_name = part[1:-1]
                                        f.write(f"      - name: {param_name}\n")
                                        f.write("        in: path\n")
                                        f.write("        required: true\n")
                                        f.write("        type: integer\n")
                                        f.write(f"        description: ID of the {param_name}\n")
                            
                            # Add request body if POST/PUT
                            if method in ["POST", "PUT", "PATCH"]:
                                f.write("    parameters:\n")
                                f.write("      - name: body\n")
                                f.write("        in: body\n")
                                f.write("        required: true\n")
                                f.write("        schema:\n")
                                f.write("          type: object\n")
                                f.write("          properties:\n")
                                f.write("            # Add properties here\n")
                                
                            # Add responses
                            f.write("    responses:\n")
                            if method == "DELETE":
                                f.write("      204:\n")
                                f.write("        description: No Content\n")
                            elif method in ["POST", "PUT", "PATCH"]:
                                if method == "POST":
                                    f.write("      201:\n")
                                else:
                                    f.write("      200:\n")
                                f.write("        description: Success\n")
                                f.write("        schema:\n")
                                f.write("          type: object\n")
                                f.write("          properties:\n")
                                f.write("            # Add properties here\n")
                            else:  # GET
                                f.write("      200:\n")
                                f.write("        description: Success\n")
                                f.write("        schema:\n")
                                f.write("          type: object\n")
                                f.write("          properties:\n")
                                f.write("            # Add properties here\n")
                            
                            # Add error responses
                            f.write("      400:\n")
                            f.write("        description: Bad Request\n")
                            f.write("      401:\n")
                            f.write("        description: Unauthorized\n")
                            f.write("      404:\n")
                            f.write("        description: Not Found\n")
                            f.write("```\n\n")
            
            print(f"\nDocumentation report generated: {output_file}")
            
    def _operation_id_from_path(self, path, method):
        """Generate an operation ID from path and method"""
        # Remove /api/ prefix
        if path.startswith('/api/'):
            path = path[5:]
        elif path.startswith('/'):
            path = path[1:]
            
        # Remove trailing slash    
        if path.endswith('/'):
            path = path[:-1]
            
        # Replace path parameters with 'by_id'
        parts = path.split('/')
        operation_parts = []
        for part in parts:
            if part.startswith('{') and part.endswith('}'):
                continue  # Skip path parameters
            elif part.isdigit():
                continue  # Skip IDs
            else:
                operation_parts.append(part)
                
        # Join the parts
        operation = '_'.join(operation_parts)
        
        # Add method prefix
        method_prefixes = {
            'GET': 'get',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'partial_update',
            'DELETE': 'delete'
        }
        
        prefix = method_prefixes.get(method, method.lower())
        
        # Handle special cases for nested resources
        if len(operation_parts) > 1:
            if method.lower() == 'post':
                return f"create_{operation_parts[-1]}_for_{operation_parts[0]}"
            elif method.lower() == 'get':
                if operation_parts[-1] == operation_parts[0]:
                    return f"get_{operation_parts[0]}_detail"
                else:
                    return f"get_{operation_parts[-1]}_for_{operation_parts[0]}"
            else:
                return f"{prefix}_{operation}"
        else:
            if method.lower() == 'get':
                return f"get_{operation}_list"
            else:
                return f"{prefix}_{operation}"
    
    def validate_documentation_vs_implementation(self):
        """Validate that all tested endpoints are documented in the Swagger schema"""
        result = {
            "validated": True,
            "issues": []
        }
        
        # Extract documented endpoints from Swagger schema
        documented_endpoints = set()
        for path, methods in self.swagger.get('paths', {}).items():
            for method in methods.keys():
                if method.lower() != 'parameters':  # Skip parameters section
                    documented_endpoints.add((path, method.lower()))
        
        # Check if all tested endpoints are documented
        for test_result in self.test_results["details"]:
            endpoint = test_result["endpoint"]
            method = test_result["method"].lower()
            
            # Normalize endpoint for comparison
            if endpoint.startswith('/api'):
                endpoint = endpoint[4:]  # Remove /api prefix
                
            # Check if endpoint exists in documentation
            endpoint_found = False
            for doc_path, doc_method in documented_endpoints:
                # Normalize path for comparison (replace numeric IDs with {id})
                doc_parts = doc_path.split('/')
                endpoint_parts = endpoint.split('/')
                
                if len(doc_parts) != len(endpoint_parts):
                    continue
                
                match = True
                for i, (doc_part, endpoint_part) in enumerate(zip(doc_parts, endpoint_parts)):
                    if doc_part != endpoint_part:
                        # Check if it's a path parameter (e.g., {id})
                        if (doc_part.startswith('{') and doc_part.endswith('}')) and endpoint_part.isdigit():
                            continue
                        match = False
                        break
                
                if match and method == doc_method:
                    endpoint_found = True
                    break
            
            if not endpoint_found:
                result["validated"] = False
                result["issues"].append(f"Endpoint exists but not documented: {test_result['method']} {test_result['endpoint']}")
        
        return result
    
    def get_headers(self):
        """Get request headers with auth token if available"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def test_registration(self):
        """Test user registration"""
        endpoint = "/api/auth/register/"
        method = "POST"
        
        # Generate unique email to avoid conflicts
        timestamp = int(time.time())
        test_data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "full_name": "Test User",
            "password": "securepassword123",
            "confirm_password": "securepassword123"
        }
        
        logger.info(f"Testing {method} {endpoint}")
        response = requests.post(urljoin(self.base_url, endpoint), json=test_data)
        
        expected_codes = [201]
        result = self._track_result(endpoint, method, response.status_code, expected_codes, response)
        
        if result["passed"]:
            logger.info(f"✅ {method} {endpoint} - {response.status_code}")
            return test_data
        else:
            logger.error(f"❌ {method} {endpoint} - {response.status_code}")
            return None
    
    def test_login(self, email, password):
        """Test user login"""
        endpoint = "/api/auth/login/"
        method = "POST"
        
        test_data = {
            "email": email,
            "password": password
        }
        
        logger.info(f"Testing {method} {endpoint}")
        response = requests.post(urljoin(self.base_url, endpoint), json=test_data)
        
        expected_codes = [200]
        result = self._track_result(endpoint, method, response.status_code, expected_codes, response)
        
        if result["passed"]:
            logger.info(f"✅ {method} {endpoint} - {response.status_code}")
            resp_data = response.json()
            self.token = resp_data.get('access', None)
            return self.token
        else:
            logger.error(f"❌ {method} {endpoint} - {response.status_code}")
            return None
    
    def test_get_current_user(self):
        """Test getting current user info"""
        endpoint = "/api/auth/me/"
        method = "GET"
        
        logger.info(f"Testing {method} {endpoint}")
        response = requests.get(
            urljoin(self.base_url, endpoint), 
            headers=self.get_headers()
        )
        
        expected_codes = [200]
        result = self._track_result(endpoint, method, response.status_code, expected_codes, response)
        
        if result["passed"]:
            logger.info(f"✅ {method} {endpoint} - {response.status_code}")
            resp_data = response.json()
            self.user_id = resp_data.get('id', None)
            return resp_data
        else:
            logger.error(f"❌ {method} {endpoint} - {response.status_code}")
            return None
    
    def test_create_post(self):
        """Test creating a post"""
        endpoint = "/api/posts/"
        method = "POST"
        
        test_data = {
            "content": f"Test post content at {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "code_snippet": "print('Hello, world!')"
        }
        
        logger.info(f"Testing {method} {endpoint}")
        response = requests.post(
            urljoin(self.base_url, endpoint), 
            json=test_data,
            headers=self.get_headers()
        )
        
        expected_codes = [201]
        result = self._track_result(endpoint, method, response.status_code, expected_codes, response)
        
        if result["passed"]:
            logger.info(f"✅ {method} {endpoint} - {response.status_code}")
            resp_data = response.json()
            self.post_id = resp_data.get('id', None)
            return resp_data
        else:
            logger.error(f"❌ {method} {endpoint} - {response.status_code}")
            return None
    
    def test_create_comment(self):
        """Test creating a comment on a post"""
        if not self.post_id:
            logger.warning("Skipping create comment test - no post ID available")
            self.test_results["skipped"] += 1
            return None
            
        endpoint = f"/api/posts/{self.post_id}/comments/"
        method = "POST"
        
        test_data = {
            "content": f"Test comment at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        logger.info(f"Testing {method} {endpoint}")
        response = requests.post(
            urljoin(self.base_url, endpoint), 
            json=test_data,
            headers=self.get_headers()
        )
        
        expected_codes = [201]
        result = self._track_result(endpoint, method, response.status_code, expected_codes, response)
        
        if result["passed"]:
            logger.info(f"✅ {method} {endpoint} - {response.status_code}")
            resp_data = response.json()
            self.comment_id = resp_data.get('id', None)
            return resp_data
        else:
            logger.error(f"❌ {method} {endpoint} - {response.status_code}")
            return None
    
    def test_like_post(self):
        """Test liking a post"""
        if not self.post_id:
            logger.warning("Skipping like post test - no post ID available")
            self.test_results["skipped"] += 1
            return None
            
        endpoint = f"/api/posts/{self.post_id}/like/"
        method = "POST"
        
        logger.info(f"Testing {method} {endpoint}")
        response = requests.post(
            urljoin(self.base_url, endpoint),
            headers=self.get_headers()
        )
        
        expected_codes = [201]
        result = self._track_result(endpoint, method, response.status_code, expected_codes, response)
        
        if result["passed"]:
            logger.info(f"✅ {method} {endpoint} - {response.status_code}")
            return True
        else:
            logger.error(f"❌ {method} {endpoint} - {response.status_code}")
            return False
    
    def test_unlike_post(self):
        """Test unliking a post"""
        if not self.post_id:
            logger.warning("Skipping unlike post test - no post ID available")
            self.test_results["skipped"] += 1
            return None
            
        endpoint = f"/api/posts/{self.post_id}/unlike/"
        method = "DELETE"
        
        logger.info(f"Testing {method} {endpoint}")
        response = requests.delete(
            urljoin(self.base_url, endpoint),
            headers=self.get_headers()
        )
        
        expected_codes = [204]
        result = self._track_result(endpoint, method, response.status_code, expected_codes, response)
        
        if result["passed"]:
            logger.info(f"✅ {method} {endpoint} - {response.status_code}")
            return True
        else:
            logger.error(f"❌ {method} {endpoint} - {response.status_code}")
            return False
    
    def test_get_notifications(self):
        """Test getting notifications"""
        endpoint = "/api/notifications/"
        method = "GET"
        
        logger.info(f"Testing {method} {endpoint}")
        response = requests.get(
            urljoin(self.base_url, endpoint),
            headers=self.get_headers()
        )
        
        expected_codes = [200]
        result = self._track_result(endpoint, method, response.status_code, expected_codes, response)
        
        if result["passed"]:
            logger.info(f"✅ {method} {endpoint} - {response.status_code}")
            resp_data = response.json()
            if 'results' in resp_data and resp_data['results']:
                self.notification_id = resp_data['results'][0].get('id', None)
            return resp_data
        else:
            logger.error(f"❌ {method} {endpoint} - {response.status_code}")
            return None
    
    def test_create_project(self):
        """Test creating a project"""
        endpoint = "/api/projects/"
        method = "POST"
        
        test_data = {
            "title": f"Test Project {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "description": "This is a test project created by the API tester",
            "repo_url": "https://github.com/test/test-project",
            "tech_stack_ids": [],
            "status": "active"
        }
        
        logger.info(f"Testing {method} {endpoint}")
        response = requests.post(
            urljoin(self.base_url, endpoint),
            json=test_data,
            headers=self.get_headers()
        )
        
        expected_codes = [201]
        result = self._track_result(endpoint, method, response.status_code, expected_codes, response)
        
        if result["passed"]:
            logger.info(f"✅ {method} {endpoint} - {response.status_code}")
            resp_data = response.json()
            self.project_id = resp_data.get('id', None)
            return resp_data
        else:
            logger.error(f"❌ {method} {endpoint} - {response.status_code}")
            return None
    
    def test_notification_settings(self):
        """Test notification settings"""
        endpoint = "/api/notifications/settings/"
        method = "GET"
        
        logger.info(f"Testing {method} {endpoint}")
        response = requests.get(
            urljoin(self.base_url, endpoint),
            headers=self.get_headers()
        )
        
        expected_codes = [200]
        result = self._track_result(endpoint, method, response.status_code, expected_codes, response)
        
        if result["passed"]:
            logger.info(f"✅ {method} {endpoint} - {response.status_code}")
            get_result = response.json()
            
            # Now test updating settings
            method = "PUT"
            settings_data = {
                "email_likes": False,
                "email_comments": False,
                "email_follows": True,
                "email_mentions": True,
                "email_project_invites": True,
                "email_project_requests": True,
                "push_likes": True,
                "push_comments": True,
                "push_follows": True,
                "push_mentions": True,
                "push_project_invites": True,
                "push_project_requests": True
            }
            
            logger.info(f"Testing {method} {endpoint}")
            response = requests.put(
                urljoin(self.base_url, endpoint),
                json=settings_data,
                headers=self.get_headers()
            )
            
            result = self._track_result(endpoint, method, response.status_code, expected_codes, response)
            if result["passed"]:
                logger.info(f"✅ {method} {endpoint} - {response.status_code}")
                return response.json()
            else:
                logger.error(f"❌ {method} {endpoint} - {response.status_code}")
                return None
        else:
            logger.error(f"❌ {method} {endpoint} - {response.status_code}")
            return None
    
    def run_all_tests(self):
        """Run all API tests in sequence"""
        logger.info("Starting API tests")
        
        # Test authentication
        user_data = self.test_registration()
        if user_data:
            self.test_login(user_data["email"], user_data["password"])
        else:
            # Try a fallback login with default credentials
            self.test_login("test@example.com", "password")
        
        # Only continue if logged in
        if self.token:
            # Get user info
            self.test_get_current_user()
            
            # Test posts
            self.test_create_post()
            self.test_like_post()
            self.test_unlike_post()
            
            # Test comments
            self.test_create_comment()
            
            # Test notifications
            self.test_get_notifications()
            
            # Test projects
            self.test_create_project()
            
            # Test notification settings
            self.test_notification_settings()
            
            # Add more test cases here
        else:
            logger.error("Authentication failed, skipping remaining tests")
        
        # Report results
        self.report_results()
        
        return self.test_results


if __name__ == "__main__":
    base_url = "http://localhost:8050"
    swagger_path = "api_schema.json"
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    if len(sys.argv) > 2:
        swagger_path = sys.argv[2]
    
    tester = ApiTester(base_url, swagger_path)
    tester.run_all_tests() 