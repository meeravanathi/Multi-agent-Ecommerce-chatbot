from groq_llm import GroqLLM
from agents.order_agent import OrderAgent
from agents.product_agent import ProductAgent
from agents.support_agent import SupportAgent
from agents.weather_agent import WeatherAgent
import json

class RouterAgent:
    def __init__(self):
        self.llm = GroqLLM()
        self.agents = {
            "order": OrderAgent(),
            "product": ProductAgent(),
            "support": SupportAgent(),
            "weather": WeatherAgent()
        }
        
    def route_query(self, user_query: str, context: dict = None) -> dict:
        """Route user query to appropriate agent"""
        
        routing_prompt = f"""
        Analyze this customer query and determine which agent should handle it:
        
        Query: "{user_query}"
        
        Available agents:
        1. order - handles order status, tracking, cancellations (keywords: order, track, cancel, shipping, delivery)
        2. product - handles product search, details, availability (keywords: product, item, buy, price, stock, available)
        3. support - handles general support, FAQ, complaints (keywords: help, support, problem, issue, refund, return, policy)
        4. weather - handles weather queries (keywords: weather, temperature, forecast, climate)
        
        Consider the main intent and keywords.
        **Output ONLY the JSON below, without any explanation or text:**
       
        {{
            "agent": "agent_name",
            "confidence": 0.95,
            "reasoning": "brief explanation"
        }}
        """
        
        routing_result = self.llm._call(routing_prompt)
        
        try:
            routing_decision = json.loads(routing_result)
            selected_agent = routing_decision.get("agent", "support")
            confidence = routing_decision.get("confidence", 0.5)
            
            # Route to selected agent
            if selected_agent in self.agents:
                agent_response = self.agents[selected_agent].process(user_query, context)
                agent_response["routing"] = {
                    "selected_agent": selected_agent,
                    "confidence": confidence,
                    "reasoning": routing_decision.get("reasoning", "")
                }
                return agent_response
            else:
               
                return self.agents["support"].process(user_query, context)
                
        except json.JSONDecodeError:

            return self.agents["support"].process(user_query, context)
    
    def list_capabilities(self) -> dict:
        """List all available capabilities"""
        capabilities = {}
        for agent_name, agent in self.agents.items():
            capabilities[agent_name] = {
                "name": agent.name,
                "description": agent.description
            }
        
        return {
            "agent": "Router Agent",
            "response": "Here are my capabilities:",
            "capabilities": capabilities,
            "success": True
        }