from typing import List
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.models.enums import ApplicationStatus
from src.models.models import Application


def get_application_by_id(db: Session, application_id: int) -> Application:
    return db.query(Application).filter(Application.application_id == application_id).first()


def get_all_applications(db: Session) -> List[Application]:
    return db.query(Application).all()


def get_all_applications_by_client(db: Session, client_id: int) -> List[Application]:
    return db.query(Application).filter(Application.client_id == client_id).all()


def get_status_of_application_by_id(db: Session, application_id: int) -> ApplicationStatus:
    return ApplicationStatus[db.query(Application).filter(Application.application_id == application_id).first().status]


def create_application(db: Session, db_application: Application) -> int:
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application.application_id


def delete_application(db: Session, application_id: int) -> Application:
    application = get_application_by_id(db, application_id)
    db.delete(application)
    db.commit()
    db.close()
    return application


def update_status_of_application(db: Session, application_id: int, new_status: ApplicationStatus):
    application = get_application_by_id(db, application_id)
    if not application:
        return
    application.status = new_status.name
    db.commit()
    db.refresh(application)
    return 