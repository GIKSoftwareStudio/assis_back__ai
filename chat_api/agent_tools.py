from datetime import datetime
import json
import os
import requests
def get_current_time()-> str:
    """Returns the actual current date and time of the server."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def search_internet(query: str)-> str:
    """Simulates a web search and returns a hardcoded summary of search results."""
    return f"Mock search results for '{query}': Found multiple relevant discussions, articles, and product reviews online matching this query."


def get_categories() -> str:
    """"Get all product categories from the store API."""
    base_url = os.getenv("STORE_API_BASE_URL")
    if not base_url:
        return "Error: STORE_API_BASE_URL is not configured"
    try:
        response = requests.get(
            f"{base_url}/categories",
            timeout = 15
        )
        response.raise_for_status()
        categories = response.json()
        return json.dumps(categories, ensure_ascii=False)
    except requests.RequestException as e:
        return f"Error fetching categories: {str(e)}"
    except ValueError:
        return "Error: The categories API returned invalid JSON."



def search_products(
        query: str = None,
            category_id: int = None,
            min_price: float = None,
            max_price: float = None,
            sort_by: str = None,
            order: str = "asc",
            limit: int = 5
) -> str:
    """Search products and filter them by category and price."""
    base_url = os.getenv("STORE_API_BASE_URL")
    if not base_url:
        return "Error: STORE_API_BASE_URL is not configured."
    try:
        params = {}
        if category_id is not None:
            params["category_id"] = category_id
        response = requests.get(
            f"{base_url}/products",
            params=params,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])
        next_url = data.get("links", {}).get("next")
        while next_url:
            response = requests.get(next_url, timeout=15)
            response.raise_for_status()
            data = response.json()
            products.extend(data.get("products", []))
            next_url = data.get("links", {}).get("next")
        if query:
            products = [
                p for p in products
                if query.lower() in p.get("title", "").lower()
            ]
        if min_price is not None:
            products = [
                p for p in products
                if p.get("price", 0) >= min_price
            ]
        if max_price is not None:
            products = [
                p for p in products
                if p.get("price", 0) <= max_price
            ]
        if sort_by == "price":
            products.sort(
                key=lambda p: p.get("price", 0),
                reverse=(order == "desc")
            )
        total_found = len(products)
        products = products[:max(1, min(limit, 20))]
        return json.dumps(
            {
                "total_found": total_found,
                "products": products
            },
            ensure_ascii=False
        )
    except requests.RequestException as error:
        return f"Error searching products: {str(error)}"
    except (ValueError, TypeError):
        return "Error: Invalid response from products API."
        
   

def get_product_details(product_id: int) -> str:
    """Get detailed information about a product using its ID."""
    base_url = os.getenv("STORE_API_BASE_URL")
    if not base_url:
        return "Error: STORE_API_BASE_URL is not configured."
    try:
        response = requests.get(
            f"{base_url}/products/{product_id}",
            timeout=15
        )
        response.raise_for_status()
        product = response.json()
        return json.dumps(product, ensure_ascii=False)
    except requests.HTTPError as error:
        if response.status_code == 404:
            return f"Error: Product with ID {product_id} was not found."
        return f"Error fetching product details: {str(error)}"
    except requests.RequestException as error:
        return f"Error connecting to store API: {str(error)}"
    except ValueError:
        return "Error: The product API returned invalid JSON."





def recommend_products(
        query: str,
        max_price: float,
        category_id: int = None,
        limit: int = 5
) -> str:
    """Recommend available store products within the user's budget."""
    try:
        result = search_products(
            query=query,
            category_id=category_id,
            max_price=max_price,
            sort_by="price",
            order="asc",
            limit=limit
        )
        data = json.loads(result)
        if "Error" in result:
            return result
        products = data.get("products", [])
        products = [
            product for product in products
            if product.get("stock", 0) > 0
        ]
        if not products:
            return json.dumps(
                {
                    "message": "No available products were found within the specified budget.",
                    "budget": max_price,
                    "currency": "Toman",
                    "products": []
                }, ensure_ascii=False)
        return json.dumps(
            {
                "message": "Recommended products within the user's budget.",
                "budget": max_price,
                "currency": "Toman",
                "total_found": len(products),
                "products": products
            }, ensure_ascii=False)
    except (ValueError, TypeError) as error:
        return f"Error generating recommendations: {str(error)}"
    
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
    "get_store_policies": get_store_policies,
    "get_categories": get_categories,
    "search_products": search_products,
    "get_product_details": get_product_details,


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
        "function":{
            "name": "get_categories",
            "description": "Retrieve all available product categories from the store. Use this to identify the correct category before searching for products.",
            "parameters":{
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function":{
            "name": "search_products",
            "description": "Search store products by title, category, and budget. Can sort products by price.",
            "parameters":{
                "type": "object",
                "properties":{
                    "query":{
                        "type": "string",
                        "description": "Product name or search keyword."
                    },
                    "category_id":{
                        "type": "integer",
                        "description": "Category ID obtained from get_categories."
                    },
                    "min_price":{
                        "type": "number",
                        "description": "Minimum product price."
                    },
                    "max_price":{
                        "type": "number",
                        "description": "Maximum product price or user budget."
                    },
                    "sort_by":{
                        "type": "string",
                        "enum": ["price"],
                        "description": "Sort products by price."
                    },
                    "order":{
                        "type": "string",
                        "enum": ["asc", "desc"],
                        "description": "Ascending or descending order."
                    },
                    "limit":{
                        "type": "integer",
                        "description": "Maximum number of returned products."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function":{
            "name": "get_product_details",
            "description": "Get complete details of a specific store product using its product ID.",
            "parameters":{
                "type": "object",
                "properties":{
                    "product_id":{
                        "type": "integer",
                        "description": "The unique ID of the product."
                    }
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_products",
            "description": (
                "Recommend real available products from the store based on "
                "the user's natural-language request and maximum budget in Toman. "
                "Use get_categories first when category identification is needed. "
                "Only recommend products that are in stock and within budget."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query":{
                        "type": "string",
                        "description": "The product name or keywords describing what the user wants."
                    },
                    "max_price": {
                        "type": "number",
                        "description": "The user's maximum budget in Toman."
                    },
                    "category_id": {
                        "type": "integer",
                        "description": "The relevant category ID from get_categories, if known."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of products to recommend. Default is 5."
                    }
                },
                "required": ["query", "max_price"]
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
