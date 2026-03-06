from fastapi import FastAPI

app=FastAPI()

@app.get("/")
def read_root():
    return {"message":"home page. nothing to see here"}


products = [
    {"id": 1, "name": "Art Kit", "price": 100, "category": "Stationery", "in_stock": True},
    {"id": 2, "name": "Wireless Mouse", "price": 769, "category": "Electronics", "in_stock": False},
    {"id": 3, "name": "Bookmarks", "price": 4900, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "USB", "price": 199, "category": "Electronics", "in_stock": False},  
]


#Q1

new_product=[
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False}
]

products+=new_product

@app.get("/products")
def get_prod():
    return {"products": products, "total": len(products)}

#Q2

@app.get("/products/category/{category_name}")
def get_prod_by_cat(category_name: str):
    if category_name.lower() not in [product["category"].lower() for product in products]:
        return {"error": "No products found in this category"}

    filtered_products = [product for product in products if product["category"].lower() == category_name.lower()]
    return {"products": filtered_products, "total": len(filtered_products)}


#Q3
@app.get("/products/instock")
def get_prod_in_stock():
    in_stock_products = [product for product in products if product["in_stock"]]
    return {"products": in_stock_products, "total": len(in_stock_products)}


#Q4

@app.get("/store/summary")
def store_summary():

    in_stock_count = len([product for product in products if product["in_stock"]])
    out_stock_count = len(products) - in_stock_count

    categories = list(set([product["category"] for product in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": categories
    }


#Q5

@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    results = [
        product for product in products
        if keyword.lower() in product["name"].lower()
    ]

    if not results:
        return {"message": "No products matched your search"}

    return {
        "keyword": keyword,
        "results": results,
        "total_matches": len(results)
    }

#Q6 bonsu
@app.get("/products/deals")
def get_deals():
    
    min_price_product = min(products, key=lambda x: x["price"])
    max_price_product = max(products, key=lambda x: x["price"])
    return {
        "best_deal": min_price_product,
        "premium_deal": max_price_product
    }

