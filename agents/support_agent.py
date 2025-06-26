from groq_llm import GroqLLM
from tools.support_tools import SupportTools
import json
from pydantic import BaseModel
class SupportAgent:
    def __init__(self):
        self.llm = GroqLLM()
        self.tools = SupportTools()
        self.name = "Support Agent"
        self.description = "Handles general support, FAQs, and ticket creation"
    
    def process(self, query: str, context: dict = None) -> dict:
        """Process support-related queries"""
        
        analysis_prompt = f"""
        Analyze this customer support query:
        Query: "{query}"
        
        Determine the action needed:
        1. faq_answer - if asking about common topics (shipping, returns, warranty, payment)
        2. create_ticket - if reporting an issue that needs human attention
        3. escalate - if customer is frustrated or needs human agent
        4. general_help - for general support questions
        
        Extract FAQ topic if relevant.
        Determine if customer seems frustrated (keywords: angry, frustrated, disappointed, terrible, awful).
        
        Respond in JSON format:
        {{
            "action": "action_name",
            "faq_topic": "extracted_topic_or_null",
            "frustrated": true_or_false,
            "confidence": 0.95
        }}
        """
        
        analysis_result = self.llm._call(analysis_prompt)
        
        try:
            analysis = json.loads(analysis_result)
            action = analysis.get("action")
            faq_topic = analysis.get("faq_topic")
            frustrated = analysis.get("frustrated", False)
            
            # If customer is frustrated, escalate
            if frustrated:
                return self._escalate_to_human(query)
            
            if action == "faq_answer" and faq_topic:
                result = self.tools.get_faq_answer(faq_topic)
                return self._format_response(query, result, "faq")
            
            elif action == "create_ticket":
                # For demo, create ticket with dummy email
                result = self.tools.create_support_ticket(
                    "customer@email.com", 
                    "general_inquiry", 
                    query
                )
                return self._format_response(query, result, "ticket")
            
            elif action == "escalate":
                return self._escalate_to_human(query)
            
            else:
                return self._provide_general_help(query)
                
        except json.JSONDecodeError:
            return self._provide_general_help(query)
    
    def _escalate_to_human(self, query: str) -> dict:
        """Escalate to human agent"""
        response = """I understand you need additional assistance. I'm connecting you with a human agent who can better help you with your concern. 

In the meantime, I've created a priority support ticket for you. A human representative will contact you within 2 hours.

Is there anything else I can help you with while you wait?"""
        
        # Create escalated ticket
        ticket_result = self.tools.create_support_ticket(
            "customer@email.com",
            "escalated",
            f"Escalated query: {query}"
        )
        
        return {
            "agent": self.name,
            "response": response,
            "data": ticket_result,
            "escalated": True,
            "success": True
        }
    
    def _format_response(self, query: str, result: dict, response_type: str) -> dict:
        """Format the response using LLM"""
        
        prompt = f"""
        Format a helpful support response based on this data:
        
        Customer Query: "{query}"
        Response Type: {response_type}
        Data: {json.dumps(result, indent=2)}
        in 
        Create a friendly, helpful support response. Be empathetic and professional.
        If providing FAQ info, be comprehensive but concise.
        """
        
        response = self.llm._call(prompt)
        
        return {
            "agent": self.name,
            "response": response,
            "data": result,
            "success": result.get("success", True)
        }
    
    def _provide_general_help(self, query: str) -> dict:
        """Provide general support help"""
        response = """I'm here to help with any support questions! I can assist you with:

• Shipping and delivery information
• Return and refund policies  
• Warranty information
• Payment and billing questions
• Technical support issues
• Account problems

I can also create a support ticket for complex issues or connect you with a human agent if needed.

What can I help you with today?"""
        
        return {
            "agent": self.name,
            "response": response,
            "data": {},
            "success": True
        }
