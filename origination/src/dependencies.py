from models import database


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


PRODUCT_ENGINE_URL = "http://host.docker.internal:80"
SCORING_SERVICE_URL = "unknown" # todo: replace
MIN_TIME_BETWEEN_APPLICATIONS_IN_SEC = 5 * 50 # 5 minutes