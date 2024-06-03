from fastapi import Depends, APIRouter, HTTPException
from fastapi_utils.cbv import cbv

from dependencies import get_db
from cruds import crud_clients
from models.schemas import ClientModel
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/clients",
    tags=["clients"],)


@cbv(router)
class ClientCBV:
    db: Session = Depends(get_db)
    
    
    @router.get("/{client_id}", response_model=ClientModel, summary="Get a client by their id", description="Fetches a client data by their id from the database.")
    def get_client(self, client_id: int) -> ClientModel:
        client = crud_clients.get_client_by_client_id(self.db,client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        return client


    @router.post("/", response_model=int, summary="Create a new client", description="Creates a new client.")
    def create_client(self, client: ClientModel) -> int:
        existing_client = crud_clients.get_client_by_all_data(self.db, client)
        if existing_client:
            details = {
                "message": "Client with the same info already exists",
                "client_id": existing_client.client_id,
            }
            raise HTTPException(status_code=409, detail=details)
        client = crud_clients.create_client(self.db, client)
        if not client:
            raise HTTPException(status_code=400, detail="The input is incorrect.")
        return client.client_id