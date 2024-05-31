import random
from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_db
from models.schemas import AgreementModel, AgreementRequest, AgreementResponse
from sqlalchemy.orm import Session
from cruds import crud_agreements, crud_products, crud_clients
from datetime import datetime


router = APIRouter(
    prefix="/agreement",
    tags=["agreement"],
)

# Creates a new agreement
@router.post("/", response_model=AgreementResponse, summary="Create a new agreement", description="Validate credit terms, creates a new client if non-existent before, creates a new agreement.")
def create_agreement(agreement: AgreementRequest, db: Session = Depends(get_db)) -> AgreementResponse:
    # Check if the product with the given code already exists
    product = crud_products.get_product_by_internal_code(db, agreement.product_code)
    if not product:
        raise HTTPException(status_code=400, detail="Product with the specified internal code code does not exist")

    # Check if the client with the given data already exists or create the new one
    customer = crud_clients.get_client_by_all_data(db, agreement.client)
    if customer is None:
        customer = crud_clients.create_client(db, agreement.client)
        print(customer)

    # Calculate origination amount
    origination_amount = random.uniform(product.min_origination_amount, product.max_origination_amount)
    principal_amount = agreement.disbursment_amount + origination_amount

    # Validate credit terms
    if not (product.min_loan_term <= agreement.term <= product.max_loan_term):
        raise HTTPException(status_code=400, detail=f"Agreement term should be between {product.min_loan_term} and {product.max_loan_term} месяцев")
    if not (product.min_interest_rate <= agreement.interest <= product.max_interest_rate):
        raise HTTPException(status_code=400, detail=f"Interest should be between {product.min_interest_rate} and {product.max_interest_rate}")

    # Create agreement
    new_agreement = crud_agreements.create_agreement(db, AgreementModel(
                                                            product_id=product.product_id,
                                                            client_id=customer.client_id,
                                                            term=agreement.term,
                                                            principal=principal_amount,
                                                            interest_rate=agreement.interest,
                                                            origination_amount=origination_amount,
                                                            activation_date=datetime.now(),
                                                            status="New"))
    return AgreementResponse(agreement_id=new_agreement.agreement_id)