from datetime import datetime
from typing import List
from pydantic import ValidationError
from sqlalchemy.orm import Session

from models.schemas import ClientModel
from models.models import Client
from common.repo.repository import DatabaseRepository



async def get_client_by_client_id(repo: DatabaseRepository, client_id: int) -> Client:
    client = await repo.filter(Client.client_id == client_id)
    if not client:
        return None
    return client[0]


async def get_client_by_all_data(repo: DatabaseRepository, client: ClientModel) -> Client:
    try:
        client = await repo.filter(
            Client.full_name == " ".join([client.first_name, client.third_name, client.second_name]),
            Client.birthday == datetime.strptime(client.birthday, "%d.%m.%Y").date(),
            Client.passport == client.passport_number,
        )
        if not client:
            return None
        return client[0]
    except ValueError:
        return None


async def get_all_clients(repo: DatabaseRepository) -> List[Client]:
    clients = await repo.filter()
    if not clients:
        return None
    return clients


async def create_client(repo: DatabaseRepository, client: ClientModel) -> int:
    try:
        client_data = { "full_name" : " ".join([client.first_name, client.third_name, client.second_name]),
                        "birthday" : datetime.strptime(client.birthday, "%d.%m.%Y").date(),
                        "email" : client.email,
                        "phone_number" : client.phone,
                        "passport" : client.passport_number,
                        "monthly_income" : client.salary}
    except ValidationError:
        return None
    except ValueError:
        return None
    created_client = await repo.create(client_data)
    return created_client.client_id


async def delete_client(repo: DatabaseRepository, client_id: int) -> Client:
    client = get_client_by_client_id(repo, client_id)
    if client:
        await repo.delete(Client.client_id == client_id)
        return client
    return None