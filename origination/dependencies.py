from src.models import database


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


PRODUCT_ENGINE_URL = "http://product-engine:80"
SCORING_SERVICE_URL = "unknown" # todo: replace