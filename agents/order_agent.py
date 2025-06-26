from groq_llm import GroqLLM
from tools.order_tools import OrderTools
import json

class OrderAgent:
    def __init__(self):
        self.llm = GroqLLM()
        self.tools = OrderTools()
        self.name = "Order Agent"
        self.description = "Handles order-related queries, tracking, and cancellations"
    
    def process(self, query: str, context: dict = None) -> dict:
        """Process order-related queries"""
        
        # Analyze the query to determine the action
        analysis_prompt = f"""
        Analyze this customer query about orders and determine the action needed:
        Query: "{query}"
        
        Possible actions:
        1. get_order_status - if asking about order status
        2. track_order - if asking about tracking
        3. cancel_order - if wanting to cancel
        4. general_info - if asking general order information
        
        Extract any order ID mentioned (format: ORD followed by numbers).
        
        Respond in JSON format:
        {{
            "action": "action_name",
            "order_id": "extracted_order_id_or_null",
            "confidence": 0.95
        }}
        """
        
        analysis_result = self.llm._call(analysis_prompt)
        
        try:
            analysis = json.loads(analysis_result)
            action = analysis.get("action")
            order_id = analysis.get("order_id")
            
            if action == "get_order_status" and order_id:
                result = self.tools.get_order_status(order_id)
                return self._format_response(query, result, "order_status")
            
            elif action == "track_order" and order_id:
                result = self.tools.track_order(order_id)
                return self._format_response(query, result, "tracking")
            
            elif action == "cancel_order" and order_id:
                result = self.tools.cancel_order(order_id)
                return self._format_response(query, result, "cancellation")
            
            else:
                return self._provide_general_help(query)
                
        except json.JSONDecodeError:
            return self._provide_general_help(query)
    
    def _format_response(self, query: str, result: dict, response_type: str) -> dict:
        """Format the response using LLM"""
        
        prompt = f"""
        Format a helpful customer service response based on this data:
        
        Customer Query: "{query}"
        Response Type: {response_type}
        Data: {json.dumps(result.__dict__, indent=2)}
        
        Create a friendly, helpful response. If there's an error, be apologetic and offer alternatives.
        Be concise but informative.
        """
        
        response = self.llm._call(prompt)
        
        return {
            "agent": self.name,
            "response": response,
            "data": result,
            "success": result.get("success", True)
        }
    
    def _provide_general_help(self, query: str) -> dict:
        """Provide general order help"""
        response = """I can help you with order-related questions! Here's what I can do:

• Check order status - Just provide your order ID (format: ORD001)
• Track your shipment - I'll give you tracking information
• Cancel orders - For orders still in processing status
• Answer general order questions

Please provide your order ID, or let me know how else I can help with your order!"""
        
        return {
            "agent": self.name,
            "response": response,
            "data": {},
            "success": True
        }
