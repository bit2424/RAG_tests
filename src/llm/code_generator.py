from typing import List, Dict, Any
import requests
import json

class CodeGenerator:
    def __init__(self, host: str = "localhost", port: int = 11434, 
                 model: str = "codellama:7b-instruct", parameters: dict = None):
        self.base_url = f"http://{host}:{port}"
        self.model = model
        self.parameters = parameters or {}

    def generate_code(self, table_schemas: List[Dict[str, Any]], json_structure: Dict[str, Any]) -> str:
        """Generate code based on table schemas and JSON structure."""
        prompt = self._create_prompt(table_schemas, json_structure)
        
        request_body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_gpu": self.parameters.get("num_gpu", 1),
                "num_thread": self.parameters.get("num_thread", 4),
                "temperature": self.parameters.get("temperature", 0.7),
                "top_p": self.parameters.get("top_p", 0.9),
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=request_body
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"Failed to generate code: {response.text}")

    def _create_prompt(self, table_schemas: List[Dict[str, Any]], json_structure: Dict[str, Any]) -> str:
        """Create a prompt for code generation."""
        schemas_str = json.dumps(table_schemas, indent=2)
        json_str = json.dumps(json_structure, indent=2)
        
        return f"""Given these SQL table schemas:
{schemas_str}

And this JSON structure:
{json_str}

Generate Python code that:
1. Creates SQLAlchemy models for the relevant tables
2. Includes a function to insert the JSON data into these tables
3. Handles relationships between tables appropriately

Please provide only the code without explanations.""" 