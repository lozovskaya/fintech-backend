import json
import random
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_utils.cbv import cbv

from dependencies import get_kafka_producer, get_origination_client, get_repo_dep, get_settings
from common.kafka.producer_manager import KafkaProducer
from models.schemas import AgreementModel, AgreementRequest, ApplicationRequest, KafkaProducerNewAgreementMessage
from cruds import crud_agreements, crud_products, crud_clients
from datetime import datetime

from models.enums import AgreementStatus
from clients.origination_client import OriginationClient
from models.models import Agreement, Client, Product
from common.repo.repository import DatabaseRepository


router = APIRouter(
    prefix="/agreement",
    tags=["agreement"],
)

AgreementRepository = Annotated[
    DatabaseRepository[Agreement],
    Depends(get_repo_dep(Agreement)),
]
ClientRepository = Annotated[
    DatabaseRepository[Client],
    Depends(get_repo_dep(Client)),
]
ProductRepository = Annotated[
    DatabaseRepository[Product],
    Depends(get_repo_dep(Product)),
]


@cbv(router)
class AgreementCBV:
    repo_product: ProductRepository = Depends(get_repo_dep(Product))
    repo_client: ClientRepository = Depends(get_repo_dep(Client))
    repo: AgreementRepository = Depends(get_repo_dep(Agreement))
    origination_client : OriginationClient = Depends(get_origination_client)
    kafka_producer : KafkaProducer = Depends(get_kafka_producer)

    # Creates a new agreement
    @router.post("/", response_model=int, summary="Create a new agreement", description="Validate credit terms, creates a new client if non-existent before, creates a new agreement.", status_code=status.HTTP_201_CREATED)
    async def create_agreement(self, agreement: AgreementRequest) -> int:
        # Check if the product with the given code already exists
        product = await crud_products.get_product_by_internal_code(self.repo_product, agreement.product_code)
        if not product:
            raise HTTPException(status_code=400, detail="Product with the specified internal code code does not exist")

        # Check if the client with the given data already exists or create the new one
        client = await crud_clients.get_client_by_all_data(self.repo_client, agreement.client)
        if client is None:
            client_id = await crud_clients.create_client(self.repo_client, agreement.client)
            if not client_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client info is not valid")
        else:
            client_id = client.client_id

        # Calculate origination amount
        origination_amount = random.uniform(product.min_origination_amount, product.max_origination_amount)
        principal_amount = agreement.disbursement_amount + origination_amount

        # Validate credit terms
        if not (product.min_loan_term <= agreement.term <= product.max_loan_term):
            raise HTTPException(status_code=400, detail=f"Agreement term should be between {product.min_loan_term} and {product.max_loan_term} months")
        if not (product.min_interest_rate <= agreement.interest <= product.max_interest_rate):
            raise HTTPException(status_code=400, detail=f"Interest should be between {product.min_interest_rate} and {product.max_interest_rate}")

        # Create agreement
        new_agreement = await crud_agreements.create_agreement(self.repo, AgreementModel(
                                                                product_id=product.product_id,
                                                                client_id=client_id,
                                                                term=agreement.term,
                                                                principal=principal_amount,
                                                                interest_rate=agreement.interest,
                                                                origination_amount=origination_amount,
                                                                activation_date=datetime.now(),
                                                                status=AgreementStatus.NEW.name,
                                                                disbursement_amount=agreement.disbursement_amount))
        
        # Send it to Kafka
        topicname = get_settings().kafka_topic_agreement
        await self.kafka_producer.send_message(topicname, KafkaProducerNewAgreementMessage( agreement_id=new_agreement.agreement_id,
                                                                                            client_id=client_id,
                                                                                            product_id=product.product_id,
                                                                                            disbursement_amount=agreement.disbursement_amount,
                                                                                            term=agreement.term,
                                                                                            interest=agreement.interest))
        return new_agreement.agreement_id
    
    @router.get("/{client_id}", response_model=List[int], summary="Get all active (not closed) agreements' ids by client id", description="Fetches all existing active agreements' ids from the database by the given client id.")
    async def get_all_agreements_by_client_id(self, client_id: int) -> List[int]:
        agreements = await crud_agreements.get_all_active_agreements_by_client_id(self.repo, client_id)
        if not agreements:
            return []
        
        for i in range(len(agreements)):
            agreements[i] = agreements[i].agreement_id
        
        return agreements
