from models import database
from clients.origination_client import OriginationClient
from tasks.scheduler import TasksScheduler


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

def get_origination_client():
    client = OriginationClient(base_url=ORIGINATION_URL)
    return client


def get_task_scheduler():
    return TasksScheduler(origination_client=get_origination_client())

ORIGINATION_URL = "http://host.docker.internal:90"