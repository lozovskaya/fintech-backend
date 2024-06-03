from models import database
from clients.scoring_client import ScoringClient

from tasks.scheduler import TasksScheduler

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_scoring_client():
    client = ScoringClient(base_url=SCORING_SERVICE_URL)
    return client


def get_task_scheduler():
    return TasksScheduler(scoring_client=get_scoring_client())

    
PRODUCT_ENGINE_URL = "http://host.docker.internal:80"
SCORING_SERVICE_URL = "http://host.docker.internal:8008"
MIN_TIME_BETWEEN_APPLICATIONS_IN_SEC = 5 * 50 # 5 minutes