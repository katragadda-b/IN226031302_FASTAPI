from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi import Query


#day6 continues from day 4 and 5
#this is day 4 code under this


app = FastAPI()

inventory = [
    {"id": 1, "name": "Art Kit", "price": 100, "category": "Stationery", "in_stock": True},
    {"id": 2, "name": "Wireless Mouse", "price": 769, "category": "Electronics", "in_stock": False},
    {"id": 3, "name": "Bookmarks", "price": 4900, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "USB", "price": 199, "category": "Electronics", "in_stock": False},  
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False}
]

# Q1 GET all products
@app.get("/products")
def list_products():
    return {
        "products": inventory,
        "total": len(inventory)
    }


# Q1 POST add product
@app.post("/products")
def create_product(item: dict):

    for existing in inventory:
        if existing["name"].lower() == item["name"].lower():
            raise HTTPException(status_code=400, detail="Product already exists")

    next_id = max(p["id"] for p in inventory) + 1
    item["id"] = next_id

    inventory.append(item)

    return {
        "message": "Product added",
        "product": item
    }


# Q2 PUT update product
@app.put("/products/{product_id}")
def modify_product(product_id, price=None, in_stock=None):

    product_id = int(product_id)

    if price is not None:
        price = int(price)

    if in_stock is not None:
        in_stock = in_stock.lower() == "true"

    for prod in inventory:

        if prod["id"] == product_id:

            if price is not None:
                prod["price"] = price

            if in_stock is not None:
                prod["in_stock"] = in_stock

            return {
                "message": "Product updated",
                "product": prod
            }

    raise HTTPException(status_code=404, detail="Product not found")


# Q3 DELETE product
@app.delete("/products/{product_id}")
def remove_product(product_id):

    product_id = int(product_id)

    for index, prod in enumerate(inventory):

        if prod["id"] == product_id:
            deleted_name = prod["name"]
            inventory.pop(index)

            return {
                "message": f"Product '{deleted_name}' deleted"
            }

    raise HTTPException(status_code=404, detail="Product not found")


# Q4 CRUD workflow
# (Uses POST /products, GET /products, PUT /products/{id}, DELETE /products/{id})


# Q5 GET inventory audit
@app.get("/products/audit")
def inventory_audit():

    total_products = len(inventory)

    in_stock_items = [p for p in inventory if p["in_stock"]]
    in_stock_count = len(in_stock_items)

    out_of_stock_names = [p["name"] for p in inventory if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_items)

    most_expensive = max(inventory, key=lambda x: x["price"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }


"""# GET product by id
@app.get("/products/{product_id}")
def fetch_product(product_id):

    product_id = int(product_id)

    for prod in inventory:
        if prod["id"] == product_id:
            return prod

    raise HTTPException(status_code=404, detail="Product not found")"""


# BONUS PUT category discount
@app.put("/products/discount")
def category_discount(category, discount_percent):

    discount_percent = int(discount_percent)

    modified_products = []

    for prod in inventory:
        if prod["category"].lower() == category.lower():

            new_price = int(prod["price"] * (1 - discount_percent / 100))
            prod["price"] = new_price

            modified_products.append({
                "name": prod["name"],
                "new_price": new_price
            })

    if not modified_products:
        return {"message": "No products found in this category"}

    return {
        "updated_count": len(modified_products),
        "products": modified_products
    }

# Day 5 starts here



cart = []
orders = []
order_counter = 1


# Q1 Add item to cart
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):

    product = next((p for p in inventory if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["price"]

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    subtotal = product["price"] * quantity

    cart_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "price": product["price"],
        "quantity": quantity,
        "subtotal": subtotal
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }


# Q2 View cart
@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": total
    }


# Q5 Remove item from cart
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}

    raise HTTPException(status_code=404, detail="Product not found in cart")


# Q5 Checkout
@app.post("/cart/checkout")
def checkout(customer_name: str, delivery_address: str):

    global order_counter

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")

    placed_orders = []
    grand_total = 0

    for item in cart:

        order = {
            "order_id": order_counter,
            "customer_name": customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "delivery_address": delivery_address,
            "total_price": item["subtotal"]
        }

        orders.append(order)
        placed_orders.append(order)

        grand_total += item["subtotal"]
        order_counter += 1

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": placed_orders,
        "grand_total": grand_total
    }


# Q6 View all orders
@app.get("/orders")
def get_orders():

    if not orders:
        return {"message": "No orders found"}

    return {
        "orders": orders,
        "total_orders": len(orders)
    }


#day 6 starts here




class NewProduct(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    in_stock: bool = True


class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)



def find_product(product_id: int):
    # returns product or None
    return next((p for p in inventory if p["id"] == product_id), None)


def calculate_total(product, quantity):
    return product["price"] * quantity


@app.get("/products/search")
def search_products(keyword: str = Query(...)):

    results = [p for p in inventory if keyword.lower() in p["name"].lower()]

    if not results:
        return {"message": f"No products found for: {keyword}", "results": []}

    return {
        "keyword": keyword,
        "total_found": len(results),
        "results": results
    }


@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price"),
    order: str = Query("asc")
):

    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    if order not in ["asc", "desc"]:
        return {"error": "order must be 'asc' or 'desc'"}

    reverse = order == "desc"

    sorted_list = sorted(inventory, key=lambda p: p[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_list
    }




@app.get("/products/page")
def paginate_products(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1, le=20)
):

    start = (page - 1) * limit
    paged = inventory[start:start + limit]

    return {
        "page": page,
        "limit": limit,
        "total": len(inventory),
        "total_pages": -(-len(inventory) // limit),
        "products": paged
    }
@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):

    results = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not results:
        return {"message": f"No orders found for: {customer_name}", "orders": []}

    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }


@app.get("/products/sort-by-category")
def sort_by_category():
   
    sorted_list = sorted(inventory, key=lambda p: (p["category"], p["price"]))

    return {
        "products": sorted_list,
        "total": len(sorted_list)
    }


@app.get("/products/browse")
def browse_products(
    keyword: str = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=20)
):

    result = inventory

    # Step 1: Search
    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    # Step 2: Validate sorting params
    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    if order not in ["asc", "desc"]:
        return {"error": "order must be 'asc' or 'desc'"}

    # Step 3: Sort
    reverse = (order == "desc")
    result = sorted(result, key=lambda p: p[sort_by], reverse=reverse)

    # Step 4: Pagination
    total = len(result)
    start = (page - 1) * limit
    paged = result[start:start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": -(-total // limit),
        "products": paged
    }



@app.get("/orders/page")
def get_orders_paged(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20)
):

    start = (page - 1) * limit

    return {
        "page": page,
        "limit": limit,
        "total": len(orders),
        "total_pages": -(-len(orders) // limit),
        "orders": orders[start:start + limit]
    }