from instance.database import db
from models.product import Products
from models.product_category import ProductCategories
from models.category import Categories
from models.cart_item import CartItems
from models.user import Users
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy import asc, desc, cast, Numeric, or_


def get_all_products():
    return Products.query.all()


def get_product_by_id(product_id):
    # return Products.query.get(product_id)
    return db.session.get(Products, product_id)


def get_paginated_products(page: int, limit: int):
    return Products.query.paginate(page=page, per_page=limit, error_out=False)


def create_product(data):
    print("[DEBUG] raw data:", data)
    category_ids = data.pop("category_ids", [])  # Extract category_ids
    product = Products(**data)
    db.session.add(product)
    db.session.flush()  # Assign product.id before commit

    # Create product-category mappings
    for cid in category_ids:
        db.session.add(ProductCategories(product_id=product.id, category_id=cid))

    return product


def update_product(product_id, data):
    # Replace deprecated Query.get() with Session.get()
    product = db.session.get(Products, product_id)
    if not product:
        return None
    for key, value in data.items():
        if hasattr(product, key):
            setattr(product, key, value)
    return product


def delete_product(product_id):
    # product = Products.query.get(product_id)
    product = db.session.get(Products, product_id)
    if not product:
        return None

    # ❌ REMOVE this line; let cascade handle it
    # ProductCategories.query.filter_by(product_id=product_id).delete()

    CartItems.query.filter_by(product_id=product_id).delete()
    db.session.delete(product)
    return product


from sqlalchemy.orm import aliased


def get_all_products_filtered(
    search=None,
    category_id=None,
    page=1,
    limit=10,
    sort_by="created_at",
    sort_order="desc",
    include_unapproved=False,
    only_unapproved=False,  
    current_user_id=None,
    current_user_role=None,
):
    print(f"[REPO] current_user_role={current_user_role}, user_id={current_user_id}, include_unapproved={include_unapproved}, only_unapproved={only_unapproved}")


    query = Products.query.options(
        joinedload(Products.categories_linked),
        joinedload(Products.vendor)
    )

    if current_user_role == "admin":
        if only_unapproved:
            query = query.filter(
                Products.is_approved == False,
                Products.rejected == False  # <-- Add this
            )
        elif not include_unapproved:
            query = query.filter(Products.is_approved == True)
        elif include_unapproved:
            query = query.filter(
                (Products.is_approved == False) & 
                (Products.rejected == False)  # <-- Add this
            )

    elif current_user_role == "vendor":
        print(f"[DEBUG][REPO] role=vendor, include_unapproved={include_unapproved}, only_unapproved={only_unapproved}, vendor_id={current_user_id}")
        
        if only_unapproved:
            query = query.filter(
                (Products.is_approved == False) &
                (Products.vendor_id == current_user_id)
            )
        elif include_unapproved:
            query = query.filter(
                (Products.is_approved == True) |
                (Products.vendor_id == current_user_id)
            )
        else:
            query = query.filter(Products.is_approved == True)

    else:
        
        print("[REPO] PUBLIC fallback: applying is_approved == True filter")
        query = query.filter(Products.is_approved == True)



    
# Admin: no filter


    if search:
        query = query.join(Users, Products.vendor_id == Users.id)
        query = query.filter(
            or_(
                Products.name.ilike(f"%{search}%"),
                Users.city.ilike(f"%{search}%"),
            )
        )

    if category_id:
        query = query.join(ProductCategories).filter(
            ProductCategories.category_id == category_id
        )

    if sort_by == "price":
        sort_column = cast(Products.price, Numeric)
    elif sort_by == "name":
        sort_column = Products.name
    else:
        sort_column = Products.created_at

    order_func = asc if sort_order.lower() == "asc" else desc
    query = query.order_by(order_func(sort_column))

    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    return products, total


def approve_product(product_id: int) -> Products:
    product = db.session.get(Products, product_id)
    if not product:
        return None
    product.is_approved = True
    return product
