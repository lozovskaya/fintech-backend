from typing import Any, List
from fastapi import Depends, APIRouter, HTTPException

from dependencies import get_db
from cruds import crud_products
from models.schemas import ProductModel
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/product",
    tags=["product"],)


# Get all products that are stored in the database
@router.get("/", response_model=list[ProductModel], summary="Get all products", description="Fetches a list of all products from the database.")
def get_products(db: Session = Depends(get_db)) -> List[ProductModel]:
    products = crud_products.get_all_products(db)
    return products

# Get a product by the internal code (example: "CL_1.0")
@router.get("/{product_code}", response_model=ProductModel, summary="Get product by internal code", description="Fetches a product by its internal code (example: 'CL_1.0') from the database.")
def get_product(product_code: str, db: Session = Depends(get_db)) -> ProductModel:
    product = crud_products.get_product_by_internal_code(db, product_code)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Get a product by id
@router.get("/id/{product_id}", response_model=ProductModel, summary="Get product by id", description="Fetches a product by its id from the database.")
def get_product_by_id(product_id: int, db: Session = Depends(get_db)) -> ProductModel:
    product = crud_products.get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Creates a new product
@router.post("/", response_model=None, summary="Create a new product", description="Creates a new product.")
def create_product(product: ProductModel, db: Session = Depends(get_db)) -> None:
    # Check if the product with the given code already exists
    existing_product = crud_products.get_product_by_internal_code(db, product.internal_code)
    if existing_product:
        raise HTTPException(status_code=409, detail="Product with this internal code already exists")
    result = crud_products.create_product(db, product)
    if result is None:
        raise HTTPException(status_code=400, detail="The input is incorrect.")
    return 

# Deletes a product if exists
@router.delete("/{product_code}", response_model=None, summary="Delete a product by internal code", description="Deletes a product.")
def delete_product(product_code: str, db: Session = Depends(get_db)) -> None:
    # Check if the product with the given code already exists
    existing_product = crud_products.get_product_by_internal_code(db, product_code)
    if existing_product is None:
        raise HTTPException(status_code=204, detail="Product not found")   
    crud_products.delete_product(db, product_code) 
    return {"status_code": 204, "detail": "Product successfully deleted"}