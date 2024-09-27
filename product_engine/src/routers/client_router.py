from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from fastapi_utils.cbv import cbv

from dependencies import get_repo_dep
from cruds import crud_clients
from models.schemas import ClientModel

from models.models import Client
from common.repo.repository import DatabaseRepository

router = APIRouter(
    prefix="/clients",
    tags=["clients"],)


ClientRepository = Annotated[
    DatabaseRepository[Client],
    Depends(get_repo_dep(Client)),
]


@cbv(router)
class ClientCBV:
    repo: ClientRepository = Depends(get_repo_dep(Client))
    
    
    @router.get("/{client_id}", response_model=ClientModel, summary="Get a client by their id", description="Fetches a client data by their id from the database.")
    async def get_client(self, client_id: int) -> ClientModel:
        client = await crud_clients.get_client_by_client_id(self.repo, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client


    @router.post("/", response_model=int, summary="Create a new client", description="Creates a new client.")
    async def create_client(self, client: ClientModel) -> int:
        existing_client = await crud_clients.get_client_by_all_data(self.repo, client)
        if existing_client:
            details = {
                "message": "Client with the same info already exists",
                "client_id": existing_client.client_id,
            }
            raise HTTPException(status_code=409, detail=details)
        client = await crud_clients.create_client(self.repo, client)
        if not client:
            raise HTTPException(status_code=400, detail="The input is incorrect.")
        return client.client_id