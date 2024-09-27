from typing import List
from pydantic import ValidationError

from models.schemas import ProductModel
from models.models import Product
from common.repo.repository import DatabaseRepository


async def get_product_by_internal_code(repo: DatabaseRepository, product_code: str) -> Product:
    product = await repo.filter(Product.internal_code == product_code)
    if not product:
        return None
    return product[0]


async def get_all_products(repo: DatabaseRepository) -> List[Product]:
    products = await repo.filter()
    if not products:
        return None
    return products

async def get_product_by_id(repo: DatabaseRepository, product_id: int) -> Product:
    product = await repo.filter(Product.product_id == product_id)
    if not product:
        return None
    return product[0]


async def create_product(repo: DatabaseRepository, product: ProductModel) -> Product:
    try:
        product_data = product.model_dump()
    except ValidationError:
        return None
    created_product = await repo.create(product_data)
    return created_product


async def delete_product(repo: DatabaseRepository, product_code: str) -> Product:
    product = await get_product_by_internal_code(repo, product_code)
    if product:
        await repo.delete(Product.product_id == product.product_id)
        return product
    return None