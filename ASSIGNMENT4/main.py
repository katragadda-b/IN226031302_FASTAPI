from fastapi import FastAPI, HTTPException


#day 5 is continues from day 4
#this is day 4 code under this


app = FastAPI()

inventory = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
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


# GET product by id
@app.get("/products/{product_id}")
def fetch_product(product_id):

    product_id = int(product_id)

    for prod in inventory:
        if prod["id"] == product_id:
            return prod

    raise HTTPException(status_code=404, detail="Product not found")


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


# -----------------------------
# CART STORAGE
# -----------------------------
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