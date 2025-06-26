from typing import Dict, Any
from datetime import datetime

class SupportTools:
    def __init__(self):
        self.tickets = {}
        self.ticket_counter = 1
        self.faq = {
            "shipping": "We offer free shipping on orders over $50. Standard shipping takes 3-5 business days.",
            "returns": "You can return items within 30 days of purchase for a full refund.",
            "warranty": "All electronics come with a 1-year manufacturer warranty.",
            "payment": "We accept all major credit cards, PayPal, and Apple Pay."
        }
    
    def create_support_ticket(self, customer_email: str, issue_type: str, description: str) -> Dict[str, Any]:
        """Create a new support ticket"""
        ticket_id = f"TICK{self.ticket_counter:04d}"
        self.ticket_counter += 1
        
        ticket = {
            "id": ticket_id,
            "customer_email": customer_email,
            "issue_type": issue_type,
            "description": description,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "priority": "medium"
        }
        
        self.tickets[ticket_id] = ticket
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "message": f"Support ticket {ticket_id} created successfully"
        }
    
    def get_faq_answer(self, topic: str) -> Dict[str, Any]:
        """Get FAQ answer for a topic"""
        topic_lower = topic.lower()
        for key, answer in self.faq.items():
            if key in topic_lower or topic_lower in key:
                return {
                    "success": True,
                    "topic": key,
                    "answer": answer
                }
        
        return {
            "success": False,
            "message": "FAQ topic not found. Available topics: shipping, returns, warranty, payment"
        }
    
    def escalate_to_human(self, ticket_id: str) -> Dict[str, Any]:
        """Escalate ticket to human agent"""
        if ticket_id in self.tickets:
            self.tickets[ticket_id]["status"] = "escalated"
            self.tickets[ticket_id]["priority"] = "high"
            return {
                "success": True,
                "message": f"Ticket {ticket_id} has been escalated to a human agent"
            }
        return {
            "success": False,
            "message": f"Ticket {ticket_id} not found"
        }
