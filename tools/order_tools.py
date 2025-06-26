from typing import Dict, Any, List
import json
from datetime import datetime, timedelta

class OrderTools:
    def __init__(self):
        # Mock database
        self.orders = {
            "ORD001": {
                "id": "ORD001",
                "customer_id": "CUST001",
                "items": [{"name": "Laptop", "quantity": 1, "price": 999.99}],
                "status": "shipped",
                "tracking_number": "TRK123456789",
                "order_date": "2024-01-15",
                "estimated_delivery": "2024-01-20"
            },
            "ORD002": {
                "id": "ORD002",
                "customer_id": "CUST002",
                "items": [{"name": "Phone", "quantity": 1, "price": 699.99}],
                "status": "processing",
                "tracking_number": None,
                "order_date": "2024-01-18",
                "estimated_delivery": "2024-01-25"
            }
        }
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status by order ID"""
        order = self.orders.get(order_id.upper())
        if order:
            return {
                "success": True,
                "order": order
            }
        return {
            "success": False,
            "message": f"Order {order_id} not found"
        }
    
    def track_order(self, order_id: str) -> Dict[str, Any]:
        """Track order by order ID"""
        order = self.orders.get(order_id.upper())
        if order and order.get("tracking_number"):
            return {
                "success": True,
                "tracking_info": {
                    "tracking_number": order["tracking_number"],
                    "status": order["status"],
                    "estimated_delivery": order["estimated_delivery"]
                }
            }
        elif order:
            return {
                "success": True,
                "message": "Order is being processed. Tracking number will be available soon."
            }
        return {
            "success": False,
            "message": f"Order {order_id} not found"
        }
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order"""
        order = self.orders.get(order_id.upper())
        if order:
            if order["status"] == "processing":
                order["status"] = "cancelled"
                return {
                    "success": True,
                    "message": f"Order {order_id} has been cancelled successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Order {order_id} cannot be cancelled (Status: {order['status']})"
                }
        return {
            "success": False,
            "message": f"Order {order_id} not found"
        }