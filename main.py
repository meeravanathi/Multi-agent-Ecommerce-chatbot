from router_agent import RouterAgent
import json

class EcommerceCustomerService:
    def __init__(self):
        self.router = RouterAgent()
        self.conversation_history = []
    
    def chat(self, user_input: str) -> dict:
        """Main chat interface"""
        
        # Add user input to conversation history
        self.conversation_history.append({
            "role": "user",
            "message": user_input,
            "timestamp": self._get_timestamp()
        })
        
        # Route query to appropriate agent
        response = self.router.route_query(user_input, {
            "history": self.conversation_history[-5:]  # Last 5 messages for context
        })
        
        # Add response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "message": response.get("response", ""),
            "agent": response.get("agent", "Unknown"),
            "timestamp": self._get_timestamp()
        })
        
        return response
    
    def get_capabilities(self) -> dict:
        """Get system capabilities"""
        return self.router.list_capabilities()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def print_response(self, response: dict):
        """Pretty print response"""
        print(f"\n{'='*50}")
        print(f"Agent: {response.get('agent', 'Unknown')}")
        print(f"{'='*50}")
        print(response.get('response', 'No response'))
        
        if response.get('routing'):
            routing = response['routing']
            print(f"\n[Routing Info: {routing['selected_agent']} - Confidence: {routing['confidence']:.2f}]")
        
        print(f"{'='*50}\n")

def main():
    """Main function to run the chatbot"""
    print("🛒 E-commerce Customer Service Chatbot")
    print("Type 'quit' to exit, 'capabilities' to see what I can do")
    print("="*60)
    
    chatbot = EcommerceCustomerService()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Thank you for using our customer service! Have a great day! 👋")
                break
            
            if user_input.lower() == 'capabilities':
                response = chatbot.get_capabilities()
                chatbot.print_response(response)
                continue
            
            if not user_input:
                continue
            
            # Process the query
            response = chatbot.chat(user_input)
            chatbot.print_response(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again or type 'quit' to exit.")

# Example usage and testing
def run_examples():
    """Run example queries to demonstrate the system"""
    print("🧪 Running Example Queries")
    print("="*40)
    
    chatbot = EcommerceCustomerService()
    
    example_queries = [
        "What's the status of order ORD001?",
        "I'm looking for gaming laptops",
        "What's your return policy?",
        "What's the weather in New York?",
        "Can you cancel my order ORD002?",
        "Do you have PROD001 in stock?",
        "I need help with my account",
        "Track my order ORD001"
    ]
    
    for query in example_queries:
        print(f"\n📝 Example Query: '{query}'")
        response = chatbot.chat(query)
        chatbot.print_response(response)
        print("-" * 60)

# Agent Orchestration System
class AgentOrchestrator:
    """
    Advanced orchestration system for managing multi-agent workflows
    """
    
    def __init__(self):
        self.router = RouterAgent()
        self.active_sessions = {}
        self.workflow_templates = {
            "order_fulfillment": [
                {"agent": "product", "action": "check_availability"},
                {"agent": "order", "action": "create_order"},
                {"agent": "support", "action": "send_confirmation"}
            ],
            "issue_resolution": [
                {"agent": "support", "action": "create_ticket"},
                {"agent": "order", "action": "check_order_status"},
                {"agent": "support", "action": "provide_solution"}
            ]
        }
    
    def start_workflow(self, workflow_type: str, session_id: str, initial_data: dict) -> dict:
        """Start a multi-step workflow"""
        if workflow_type not in self.workflow_templates:
            return {"error": f"Unknown workflow type: {workflow_type}"}
        
        workflow = {
            "type": workflow_type,
            "steps": self.workflow_templates[workflow_type].copy(),
            "current_step": 0,
            "data": initial_data,
            "results": []
        }
        
        self.active_sessions[session_id] = workflow
        return self.execute_next_step(session_id)
    
    def execute_next_step(self, session_id: str) -> dict:
        """Execute the next step in the workflow"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        workflow = self.active_sessions[session_id]
        
        if workflow["current_step"] >= len(workflow["steps"]):
            return {"status": "completed", "results": workflow["results"]}
        
        current_step = workflow["steps"][workflow["current_step"]]
        agent_name = current_step["agent"]
        action = current_step["action"]
        
        # Execute step with appropriate agent
        if agent_name in self.router.agents:
            agent = self.router.agents[agent_name]
            result = agent.process(f"Execute {action}", workflow["data"])
            workflow["results"].append(result)
            workflow["current_step"] += 1
            
            return {
                "status": "step_completed",
                "step": current_step,
                "result": result,
                "next_step": workflow["current_step"] < len(workflow["steps"])
            }
        
        return {"error": f"Agent {agent_name} not found"}
    
    def get_workflow_status(self, session_id: str) -> dict:
        """Get current workflow status"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        workflow = self.active_sessions[session_id]
        return {
            "type": workflow["type"],
            "current_step": workflow["current_step"],
            "total_steps": len(workflow["steps"]),
            "progress": (workflow["current_step"] / len(workflow["steps"])) * 100,
            "results": workflow["results"]
        }

# Advanced Analytics and Monitoring
class AnalyticsManager:
    """
    Analytics system for monitoring agent performance and user interactions
    """
    
    def __init__(self):
        self.metrics = {
            "total_queries": 0,
            "agent_usage": {},
            "response_times": [],
            "success_rates": {},
            "user_satisfaction": []
        }
    
    def log_interaction(self, agent_name: str, query: str, response_time: float, 
                       success: bool, satisfaction_score: int = None):
        """Log user interaction for analytics"""
        self.metrics["total_queries"] += 1
        
        # Agent usage tracking
        if agent_name not in self.metrics["agent_usage"]:
            self.metrics["agent_usage"][agent_name] = 0
        self.metrics["agent_usage"][agent_name] += 1
        
        # Response time tracking
        self.metrics["response_times"].append(response_time)
        
        # Success rate tracking
        if agent_name not in self.metrics["success_rates"]:
            self.metrics["success_rates"][agent_name] = {"total": 0, "successful": 0}
        
        self.metrics["success_rates"][agent_name]["total"] += 1
        if success:
            self.metrics["success_rates"][agent_name]["successful"] += 1
        
        # Satisfaction tracking
        if satisfaction_score:
            self.metrics["user_satisfaction"].append(satisfaction_score)
    
    def get_analytics_report(self) -> dict:
        """Generate comprehensive analytics report"""
        avg_response_time = sum(self.metrics["response_times"]) / len(self.metrics["response_times"]) if self.metrics["response_times"] else 0
        avg_satisfaction = sum(self.metrics["user_satisfaction"]) / len(self.metrics["user_satisfaction"]) if self.metrics["user_satisfaction"] else 0
        
        success_rates = {}
        for agent, data in self.metrics["success_rates"].items():
            success_rates[agent] = (data["successful"] / data["total"]) * 100 if data["total"] > 0 else 0
        
        return {
            "total_queries": self.metrics["total_queries"],
            "agent_usage": self.metrics["agent_usage"],
            "average_response_time": round(avg_response_time, 2),
            "success_rates": success_rates,
            "average_satisfaction": round(avg_satisfaction, 2),
            "most_used_agent": max(self.metrics["agent_usage"], key=self.metrics["agent_usage"].get) if self.metrics["agent_usage"] else None
        }

# Orchestration
class EnhancedEcommerceService(EcommerceCustomerService):
  
    
    def __init__(self):
        super().__init__()
        self.orchestrator = AgentOrchestrator()
        self.analytics = AnalyticsManager()
        self.active_workflows = {}
    
    def chat_with_analytics(self, user_input: str, session_id: str = "default") -> dict:
        """Enhanced chat with analytics and orchestration support"""
        import time
        start_time = time.time()
        
        
        if user_input.lower().startswith("start workflow"):
            workflow_type = user_input.split()[-1] if len(user_input.split()) > 2 else "issue_resolution"
            return self.orchestrator.start_workflow(workflow_type, session_id, {"query": user_input})
        
        if user_input.lower() == "workflow status":
            return self.orchestrator.get_workflow_status(session_id)
        
        if user_input.lower() == "analytics":
            return {
                "agent": "Analytics Manager",
                "response": "Analytics Report Generated",
                "data": self.analytics.get_analytics_report(),
                "success": True
            }
        
        # Regular chat processing
        response = self.chat(user_input)
        
        # Log analytics
        response_time = time.time() - start_time
        self.analytics.log_interaction(
            response.get("agent", "Unknown"),
            user_input,
            response_time,
            response.get("success", False)
        )
        
        return response

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "examples":
        run_examples()
    elif len(sys.argv) > 1 and sys.argv[1] == "enhanced":
        print("🚀 Enhanced E-commerce Customer Service with Orchestration")
        service = EnhancedEcommerceService()
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    break
                
                response = service.chat_with_analytics(user_input)
                service.print_response(response)
                
            except KeyboardInterrupt:
                break
    else:
        main()