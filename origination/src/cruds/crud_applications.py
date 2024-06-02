from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc 

from models.enums import ApplicationStatus
from models.models import Application
from models.schemas import ApplicationRequest


def get_application_by_id(db: Session, application_id: int) -> Application:
    return db.query(Application).filter(Application.application_id == application_id).first()


def get_all_applications(db: Session) -> List[Application]:
    return db.query(Application).all()


def get_all_applications_by_status(db: Session, status: ApplicationStatus) -> List[Application]:
    return db.query(Application).filter(Application.status == status.name).all()


def get_all_applications_by_client(db: Session, client_id: int) -> List[Application]:
    return db.query(Application).filter(Application.client_id == client_id).order_by(desc(Application.timestamp)).all()


def get_status_of_application_by_id(db: Session, application_id: int) -> ApplicationStatus:
    return ApplicationStatus[db.query(Application).filter(Application.application_id == application_id).first().status]


def get_same_applications(db: Session, application: ApplicationRequest) -> List[Application]:
    return db.query(Application).filter(Application.client_id == application.client_id, 
                                        Application.product_id == application.product_id,
                                        Application.disbursement_amount == application.disbursment_amount,
                                        Application.term == application.term,
                                        Application.interest == application.interest).all()


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