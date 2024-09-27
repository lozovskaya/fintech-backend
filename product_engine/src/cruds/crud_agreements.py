from typing import List
from pydantic import ValidationError
from sqlalchemy.orm import Session

from models.schemas import AgreementModel
from models.models import Agreement
from models.enums import AgreementStatus



def get_agreement_by_id(db: Session, agreement_id: int) -> Agreement:
    return db.query(Agreement).filter(Agreement.agreement_id == agreement_id).first()


def get_all_agreements_by_status(db: Session, status: AgreementStatus) -> List[Agreement]:
    return db.query(Agreement).filter(Agreement.status == status.name).all()


def get_all_agreements(db: Session) -> List[Agreement]:
    return db.query(Agreement).all()


def create_agreement(db: Session, agreement: AgreementModel) -> Agreement:
    try:
        agreement_data = agreement.model_dump()
        db_agreement = Agreement(**agreement_data)
    except ValidationError as e:
        return None
    db.add(db_agreement)
    db.commit()
    db.refresh(db_agreement)
    return db_agreement


def delete_agreement(db: Session, agreement_id: int) -> Agreement:
    agreement = get_agreement_by_id(agreement_id)
    db.delete(agreement)
    db.commit()
    db.close()
    return agreement