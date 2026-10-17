from datetime import datetime
import json
def get_current_time()-> str:
    """Returns the actual current date and time of the server."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def search_internet(query: str)-> str:
    """Simulates a web search and returns a hardcoded summary of search results."""
    return f"Mock search results for '{query}': Found multiple relevant discussions, articles, and product reviews online matching this query."


def recommend_products(category: str, max_price: float = None)-> str:
    #just a test
    fake_catalog = [
        {"name": "Wireless Mechanical Keyboard", "category": "electronics", "price": 45.99, "url":"https://asgfiasgfiasgf"},
        {"name": "Ergonomic Office Chair", "category": "furniture", "price": 120.00, "url":"https://asgfiasgfiasgf"},
        {"name": "USB-C Hub Multiport Adapter", "category": "electronics", "price": 25.50, "url":"https://asgfiasgfiasgf"},
        {"name": "Stainless Steel Water Bottle", "category": "lifestyle", "price": 18.00, "url":"https://asgfiasgfiasgf"},
        {"name": "LED Desk Lamp", "category": "furniture", "price": 32.00, "url":"https://asgfiasgfiasgf"}]
    filtered = [p for p in fake_catalog if p["category"].lower() == category.lower()]
    if max_price is not None:
        filtered = [p for p in filtered if p["price"] <= max_price]
        return json.dumps(filtered if filtered else fake_catalog[:2], ensure_ascii=False)

    
def check_order_status(order_id: str) -> str:
    mock_orders = {
        "ORD-1001": "Processing",
        "ORD-1002": "Shipped",
        "ORD-1003": "Delivered",
        "ORD-1004": "Cancelled"
    }
    status = mock_orders.get(order_id.upper(), "Pending / Order ID not found in system")
    return f"Order ID {order_id} current status: {status}"


def get_store_policies(topic: str) -> str:
    policies = {
        "returns": "Our return policy allows returns within 30 days of purchase with a valid receipt. Items must be unused and in original packaging.",
        "shipping": "We offer standard shipping (3-5 business days) and express shipping (1-2 business days). Free standard shipping on orders over $50.",
        "warranty": "All electronics come with a 1-year limited manufacturer warranty covering hardware defects."
    }
    return policies.get(topic.lower(), "General store policy: Customer satisfaction is our top priority. Please contact support for specific inquiries.")

AVAILABLE_TOOLS = {
    "get_current_time": get_current_time,
    "search_internet": search_internet,
    "recommend_products": recommend_products,
    "check_order_status": check_order_status,
    "get_store_policies": get_store_policies
}
    
 

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function":{
            "name": "get_current_time",
            "description": "Get the current date and time of the server. Use this whenever the user asks for the time, day, or date.",
            "parameters":{
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_internet",
            "description": "Perform a simulated web search to look up external information, news, or general knowledge.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or keywords to look up on the web."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_products",
            "description": "Recommend products based on a specific category and an optional maximum price limit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "The product category, e.g., electronics, furniture, lifestyle."
                    },
                    "max_price": {
                        "type": "number",
                        "description": "The maximum budget or price limit for the recommended products."
                    }
                },
                "required": ["category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": "Check the shipping and processing status of a customer order using their order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The unique dummy order identifier, e.g., ORD-1001."
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_store_policies",
            "description": "Retrieve static store rules and policies regarding returns, shipping, or warranty.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The policy topic, such as 'returns', 'shipping', or 'warranty'."
                    }
                },
                "required": ["topic"]
            }
        }
    }
]
