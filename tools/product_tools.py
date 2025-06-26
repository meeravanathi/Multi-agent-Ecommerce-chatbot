from typing import Dict, Any, List

class ProductTools:
    def __init__(self):
        # Mock product database
        self.products = {
            "PROD001": {
                "id": "PROD001",
                "name": "Gaming Laptop",
                "category": "Electronics",
                "price": 1299.99,
                "in_stock": True,
                "stock_quantity": 15,
                "description": "High-performance gaming laptop with RTX 4060",
                "specifications": {
                    "RAM": "16GB",
                    "Storage": "1TB SSD",
                    "Processor": "Intel i7"
                }
            },
            "PROD002": {
                "id": "PROD002",
                "name": "Wireless Headphones",
                "category": "Electronics",
                "price": 199.99,
                "in_stock": True,
                "stock_quantity": 50,
                "description": "Premium wireless headphones with noise cancellation"
            },
            "PROD003": {
                "id": "PROD003",
                "name": "Smartphone",
                "category": "Electronics",
                "price": 699.99,
                "in_stock": False,
                "stock_quantity": 0,
                "description": "Latest flagship smartphone"
            }
        }
    
    def search_products(self, query: str) -> Dict[str, Any]:
        """Search products by name or category"""
        results = []
        query_lower = query.lower()
        
        for product in self.products.values():
            if (query_lower in product["name"].lower() or 
                query_lower in product["category"].lower() or
                query_lower in product["description"].lower()):
                results.append(product)
        
        return {
            "success": True,
            "products": results,
            "count": len(results)
        }
    
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """Get detailed product information"""
        product = self.products.get(product_id.upper())
        if product:
            return {
                "success": True,
                "product": product
            }
        return {
            "success": False,
            "message": f"Product {product_id} not found"
        }
    
    def check_availability(self, product_id: str) -> Dict[str, Any]:
        """Check product availability"""
        product = self.products.get(product_id.upper())
        if product:
            return {
                "success": True,
                "available": product["in_stock"],
                "quantity": product["stock_quantity"]
            }
        return {
            "success": False,
            "message": f"Product {product_id} not found"
        }
