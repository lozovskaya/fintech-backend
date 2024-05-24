from datetime import datetime
from typing import List
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.models.schemas import ClientModel
from src.models.models import Client


def get_client_by_client_id(db: Session, client_id: int) -> Client:
    return db.query(Client).filter(Client.client_id == client_id).first()


def get_client_by_all_data(db: Session, client: ClientModel):
    return db.query(Client).filter(
        Client.full_name == " ".join([client.first_name, client.third_name, client.second_name]),
        Client.birthday == datetime.strptime(client.birthday, "%d.%m.%Y").date(),
        Client.passport == client.passport_number,
    ).first()


def get_all_clients(db: Session) -> List[Client]:
    return db.query(Client).all()


def create_client(db: Session, client: ClientModel) -> ClientModel:
    try:
        db_client = Client(full_name=" ".join([client.first_name, client.third_name, client.second_name]),
                            birthday=datetime.strptime(client.birthday, "%d.%m.%Y").date(),
                            email=client.email,
                            phone_number=client.phone,
                            passport=client.passport_number,
                            monthly_income=client.salary)
    except ValidationError as e:
        return None
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: int) -> Client:
    client = get_client_by_client_id(client_id)
    db.delete(client)
    db.commit()
    db.close()
    return client