import random
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_utils.cbv import cbv

from dependencies import get_origination_client, get_repo_dep
from models.schemas import AgreementModel, AgreementRequest, ApplicationRequest
from cruds import crud_agreements, crud_products, crud_clients
from datetime import datetime

from models.enums import AgreementStatus
from clients.origination_client import OriginationClient
from models.models import Agreement
from common.repo.repository import DatabaseRepository


router = APIRouter(
    prefix="/agreement",
    tags=["agreement"],
)

AgreementRepository = Annotated[
    DatabaseRepository[Agreement],
    Depends(get_repo_dep(Agreement)),
]

@cbv(router)
class AgreementCBV:
    repo: AgreementRepository = Depends(get_repo_dep(Agreement))
    origination_client : OriginationClient = Depends(get_origination_client)

    # Creates a new agreement
    @router.post("/", response_model=int, summary="Create a new agreement", description="Validate credit terms, creates a new client if non-existent before, creates a new agreement.", status_code=status.HTTP_201_CREATED)
    async def create_agreement(self, agreement: AgreementRequest) -> int:
        # Check if the product with the given code already exists
        product = await crud_products.get_product_by_internal_code(self.repo, agreement.product_code)
        if not product:
            raise HTTPException(status_code=400, detail="Product with the specified internal code code does not exist")

        # Check if the client with the given data already exists or create the new one
        client = await crud_clients.get_client_by_all_data(self.repo, agreement.client)
        if client is None:
            client_id = await crud_clients.create_client(self.repo, agreement.client)
            if not client_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client info is not valid")
        else:
            client_id = client.client_id

        # Calculate origination amount
        origination_amount = random.uniform(product.min_origination_amount, product.max_origination_amount)
        principal_amount = agreement.disbursement_amount + origination_amount

        # Validate credit terms
        if not (product.min_loan_term <= agreement.term <= product.max_loan_term):
            raise HTTPException(status_code=400, detail=f"Agreement term should be between {product.min_loan_term} and {product.max_loan_term} месяцев")
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
        
        # Send it to Origination
        response = self.origination_client.post_application(ApplicationRequest(client_id=client_id,
                                                            product_id=product.product_id,
                                                            disbursement_amount=agreement.disbursement_amount,
                                                            term=agreement.term,
                                                            interest=agreement.interest))
        if not response:
            details = {
                "message": "Error: the application in Origination has not been created",
                "agreement_id": new_agreement.agreement_id,
                }
            return {"details": details}
        return new_agreement.agreement_id