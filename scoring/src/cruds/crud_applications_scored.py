from sqlalchemy.orm import Session

from models.enums import ScoringStatus
from models.models import ApplicationScored


def get_scored_application_by_application_id(db: Session, application_id: int) -> ApplicationScored:
    return db.query(ApplicationScored).filter(ApplicationScored.application_id == application_id).first()


def get_scored_application_by_scoring_id(db: Session, scoring_id: int) -> ApplicationScored:
    return db.query(ApplicationScored).filter(ApplicationScored.scoring_id == scoring_id).first()


def get_scored_status_of_application_by_application_id(db: Session, application_id: int) -> ScoringStatus:
    return ScoringStatus[db.query(ApplicationScored).filter(ApplicationScored.application_id == application_id).first().status]


def get_scored_status_of_application_by_scoring_id(db: Session, scoring_id: int) -> ScoringStatus:
    return ScoringStatus[db.query(ApplicationScored).filter(ApplicationScored.scoring_id == scoring_id).first().status]


def create_scored_application(db: Session, db_scored_application: ApplicationScored) -> int:
    db.add(db_scored_application)
    db.commit()
    db.refresh(db_scored_application)
    return db_scored_application.scoring_id


def delete_scored_application(db: Session, scoring_id: int) -> ApplicationScored:
    scored_application = get_scored_application_by_scoring_id(db, scoring_id)
    db.delete(scored_application)
    db.commit()
    db.close()
    return scored_application


def update_status_of_scored_application(db: Session, scoring_id: int, new_status: ScoringStatus):
    scored_application = get_scored_application_by_scoring_id(db, scoring_id)
    if not scored_application:
        return
    scored_application.status = new_status.name
    db.commit()
    db.refresh(scored_application)
    return 