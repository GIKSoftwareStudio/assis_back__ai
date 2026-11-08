from datetime import datetime
import json
import os

import requests


def _store_api_url(path):
    base_url = (os.getenv("STORE_API_BASE_URL") or "").rstrip("/")
    if not base_url:
        raise ValueError("STORE_API_BASE_URL is not configured")
    return f"{base_url}/{path.lstrip('/')}"


def _store_api_headers():
    token = os.getenv("STORE_API_TOKEN")
    if not token:
        raise ValueError("STORE_API_TOKEN is not configured")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


def get_current_time() -> str:
    """Return the current server date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_categories() -> str:
    """Get the public list of store categories."""
    try:
        response = requests.get(
            _store_api_url("api/categories"),
            headers={"Accept": "application/json"},
            timeout=(5, 15),
        )
        response.raise_for_status()
        payload = response.json()
        categories = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(categories, list):
            return "Error: Invalid response from categories API."
        return json.dumps(categories, ensure_ascii=False)
    except (requests.RequestException, ValueError) as error:
        return f"Error fetching categories: {error}"


def search_products(
    query: str = None,
    category_id: int = None,
    min_price: float = None,
    max_price: float = None,
    sort_by: str = None,
    order: str = "asc",
    limit: int = 5,
    page: int = 1,
) -> str:
    """Search Laravel assistant products endpoint with server-side filters."""
    try:
        per_page = max(1, min(int(limit), 50))
        page = max(1, int(page))
        params = {"per_page": per_page, "page": page}
        if query:
            params["search"] = query
        if category_id is not None:
            params["category_id"] = int(category_id)
        if min_price is not None:
            params["min_price"] = float(min_price)
        if max_price is not None:
            params["max_price"] = float(max_price)

        response = requests.get(
            _store_api_url("api/assistant/products"),
            params=params,
            headers=_store_api_headers(),
            timeout=(5, 15),
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            return "Error: Invalid response from products API."

        # Support Laravel paginator's `data` and a simple `products` response.
        products = payload.get("products", payload.get("data"))
        if not isinstance(products, list):
            return "Error: Product list is missing or invalid in API response."

        if sort_by == "price":
            products.sort(
                key=lambda item: float(item.get("price", 0)),
                reverse=(order == "desc"),
            )

        meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
        return json.dumps({
            "total_found": meta.get("total", payload.get("total", payload.get("total_found", len(products)))),
            "current_page": meta.get("current_page", payload.get("current_page", page)),
            "last_page": meta.get("last_page", payload.get("last_page", page)),
            "products": products,
        }, ensure_ascii=False)
    except (requests.RequestException, ValueError, TypeError) as error:
        return f"Error searching products: {error}"


def get_product_details(product_id: int) -> str:
    """Get one product from the public store API."""
    try:
        product_id = int(product_id)
        if product_id <= 0:
            return "Error: Product ID must be a positive integer."
        response = requests.get(
            _store_api_url(f"api/products/{product_id}"),
            headers={"Accept": "application/json"},
            timeout=(5, 15),
        )
        if response.status_code == 404:
            return "Error: Product was not found."
        response.raise_for_status()
        payload = response.json()
        product = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(product, dict):
            return "Error: Invalid response from product details API."
        return json.dumps(product, ensure_ascii=False)
    except (requests.RequestException, ValueError, TypeError) as error:
        return f"Error fetching product details: {error}"


def recommend_products(
    query: str,
    max_price: float,
    category_id: int = None,
    limit: int = 5,
    page: int = 1,
) -> str:
    """Recommend products returned by the store API within the requested budget."""
    result = search_products(
        query=query,
        category_id=category_id,
        max_price=max_price,
        sort_by="price",
        order="asc",
        limit=limit,
        page=page,
    )
    try:
        payload = json.loads(result)
    except json.JSONDecodeError:
        return result
    if not isinstance(payload, dict) or "products" not in payload:
        return result

    products = payload["products"]
    stock_field_present = all(
        "stock" in item or "quantity" in item
        for item in products
    )
    available = [
        item for item in products
        if not stock_field_present
        or float(item.get("stock", item.get("quantity", 0)) or 0) > 0
    ]
    return json.dumps({
        "message": "Products returned by the store API within the requested budget.",
        "budget": max_price,
        "products": available,
        "current_page": payload.get("current_page", page),
        "last_page": payload.get("last_page", page),
    }, ensure_ascii=False)


AVAILABLE_TOOLS = {
    "get_current_time": get_current_time,
    "get_categories": get_categories,
    "search_products": search_products,
    "get_product_details": get_product_details,
    "recommend_products": recommend_products,
}


TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time of the server.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_categories",
            "description": "Get the store's product categories.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search store products by text, category, price range, and page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Product name search text."},
                    "category_id": {"type": "integer"},
                    "min_price": {"type": "number"},
                    "max_price": {"type": "number"},
                    "sort_by": {"type": "string", "enum": ["price"]},
                    "order": {"type": "string", "enum": ["asc", "desc"]},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 50},
                    "page": {"type": "integer", "minimum": 1},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Get details for a specific product by its ID.",
            "parameters": {
                "type": "object",
                "properties": {"product_id": {"type": "integer", "minimum": 1}},
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_products",
            "description": "Find store products matching the query and maximum price; return available items when stock data is present.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_price": {"type": "number", "minimum": 0},
                    "category_id": {"type": "integer"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 50},
                    "page": {"type": "integer", "minimum": 1},
                },
                "required": ["query", "max_price"],
            },
        },
    },
]
