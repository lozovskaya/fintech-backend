from typing import Annotated, List
from fastapi import Depends, APIRouter, HTTPException
from fastapi_utils.cbv import cbv

from dependencies import get_repo_dep
from cruds import crud_products
from models.schemas import ProductModel


from common.repo.repository import DatabaseRepository
from models.models import Product

router = APIRouter(
    prefix="/product",
    tags=["product"],)

ProductRepository = Annotated[
    DatabaseRepository[Product],
    Depends(get_repo_dep(Product)),
]

@cbv(router)
class ProductCBV:
    repo: ProductRepository = Depends(get_repo_dep(Product))
    
    # Get all products that are stored in the database
    @router.get("/", response_model=list[ProductModel], summary="Get all products", description="Fetches a list of all products from the database.")
    async def get_products(self) -> List[ProductModel]:
        products = await crud_products.get_all_products(self.repo)
        return products

    # Get a product by the internal code (example: "CL_1.0")
    @router.get("/{product_code}", response_model=ProductModel, summary="Get product by internal code", description="Fetches a product by its internal code (example: 'CL_1.0') from the database.")
    async def get_product(self, product_code: str) -> ProductModel:
        product = await crud_products.get_product_by_internal_code(self.repo, product_code)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    # Get a product by id
    @router.get("/id/{product_id}", response_model=ProductModel, summary="Get product by id", description="Fetches a product by its id from the database.")
    async def get_product_by_id(self, product_id: int) -> ProductModel:
        product = await crud_products.get_product_by_id(self.repo, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    # Creates a new product
    @router.post("/", response_model=None, summary="Create a new product", description="Creates a new product.")
    async def create_product(self, product: ProductModel) -> None:
        # Check if the product with the given code already exists
        existing_product = await crud_products.get_product_by_internal_code(self.repo, product.internal_code)
        if existing_product:
            raise HTTPException(status_code=409, detail="Product with this internal code already exists")
        result = await crud_products.create_product(self.repo, product)
        if result is None:
            raise HTTPException(status_code=400, detail="The input is incorrect.")
        return 

    # Deletes a product if exists
    @router.delete("/{product_code}", response_model=None, summary="Delete a product by internal code", description="Deletes a product.")
    async def delete_product(self, product_code: str) -> None:
        # Check if the product with the given code already exists
        existing_product = await crud_products.get_product_by_internal_code(self.repo, product_code)
        if existing_product is None:
            raise HTTPException(status_code=204, detail="Product not found")   
        await crud_products.delete_product(self.repo, product_code) 
        return {"status_code": 204, "detail": "Product successfully deleted"}