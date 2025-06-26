from groq_llm import GroqLLM
from tools.product_tools import ProductTools
import json
import re

def extract_json(text: str) -> str:
    """Extract the first valid JSON block from text."""
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        return match.group(0)
    raise ValueError("No valid JSON object found in LLM response.")

class ProductAgent:
    def __init__(self):
        self.llm = GroqLLM()
        self.tools = ProductTools()
        self.name = "Product Agent"
        self.description = "Handles product searches, details, and availability"
    
    def process(self, query: str, context: dict = None) -> dict:
        """Process product-related queries"""
        
        analysis_prompt = f"""
        Analyze this customer query about products:
        Query: "{query}"
        
        Determine the action needed:
        1. search_products - if searching for products by name/category
        2. get_product_details - if asking about specific product (with ID)
        3. check_availability - if asking about stock/availability
        4. general_info - for general product questions
        
        Extract product ID if mentioned (format: PROD followed by numbers).
        Extract search terms if searching.
        
        Respond in JSON format:
        {{
            "action": "action_name",
            "product_id": "extracted_product_id_or_null",
            "search_terms": "extracted_search_terms_or_null",
            "confidence": 0.95
        }}
        """
        
        analysis_result = self.llm._call(analysis_prompt)
        
        try:
            json_text = extract_json(analysis_result)
            analysis = json.loads(json_text)
            action = analysis.get("action")
            product_id = analysis.get("product_id")
            search_terms = analysis.get("search_terms")
            
            if action == "search_products" and search_terms:
                result = self.tools.search_products(search_terms)
                return self._format_response(query, result, "search")
            
            elif action == "get_product_details" and product_id:
                result = self.tools.get_product_details(product_id)
                return self._format_response(query, result, "details")
            
            elif action == "check_availability":
                if product_id:
                    result = self.tools.check_availability(product_id)
                    return self._format_response(query, result, "availability")
                else:
                    # Try to search and check availability
                    search_result = self.tools.search_products(query)
                    return self._format_response(query, search_result, "search_availability")
            
            else:
                return self._provide_general_help(query)
                
        except json.JSONDecodeError:
            return print("Error parsing analysis result, providing general help.")
    
    def _format_response(self, query: str, result: dict, response_type: str) -> dict:
        """Format the response using LLM"""
        
        prompt = f"""
        Format a helpful product response based on this data:
        Customer Query: "{query}"
        Response Type: {response_type}
        **Output ONLY the JSON of result, without any explanation or text:**
        Data: {json.dumps(result, indent=2)}
        
        Create a friendly, informative response. If showing products, highlight key features.
        If checking availability, clearly state stock status.
        Be helpful and encourage purchase if appropriate.
        """
        
        response = self.llm._call(prompt)
        print(result)
        return {
            "agent": self.name,
            "response": response,
            "data": result,
            "success": result.get("success", True)
        }
    
    def _provide_general_help(self, query: str) -> dict:
        """Provide general product help"""
        response = """I can help you with product information! Here's what I can do:

• Search for products - Tell me what you're looking for
• Get detailed product information - Provide a product ID (PROD001, etc.)
• Check product availability and stock levels
• Compare products and features

What product information can I help you find today?"""
        
        return {
            "agent": self.name,
            "response": response,
            "data": {},
            "success": True
        }