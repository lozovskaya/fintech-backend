from typing import List
from pydantic import ValidationError
from sqlalchemy.orm import Session

from models.schemas import ProductModel
from models.models import Product


def get_product_by_internal_code(db: Session, product_code: str) -> Product:
    return db.query(Product).filter(Product.internal_code == product_code).first()


def get_all_products(db: Session) -> List[Product]:
    return db.query(Product).all()

def get_product_by_id(db: Session, product_id: int) -> Product:
    return db.query(Product).filter(Product.product_id == product_id).first()


def create_product(db: Session, product: ProductModel) -> Product:
    try:
        product_data = product.model_dump()
        db_product = Product(**product_data)
    except ValidationError as e:
        return None
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_code: str) -> Product:
    product = get_product_by_internal_code(db, product_code)
    db.delete(product)
    db.commit()
    db.close()
    return product