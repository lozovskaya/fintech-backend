from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
import requests

from dependencies import PRODUCT_ENGINE_URL, get_db
from models.models import Application
from models import enums
from models.schemas import ApplicationRequest, ApplicationResponse
from sqlalchemy.orm import Session
from cruds import crud_applications

import logging


router = APIRouter(
    prefix="/application",
    tags=["application"],
)
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def send_application_to_scoring(db: Session, application_id: int) -> None:
    scoring_response = enums.ApplicationStatus.CONFIRMED # todo: replace with a request to Scoring
    crud_applications.update_status_of_application(db, application_id, scoring_response)
    return 

# Create a new application
@router.post("/", response_model=ApplicationResponse, summary="Create an application", description="Validates product data, sends an application to Scoring service.")
async def create_application(application: ApplicationRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> ApplicationResponse:
    # Validate product data
    response = requests.get(url = PRODUCT_ENGINE_URL + f"/product/id/{application.product_id}")
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=400, detail="Product with the given ID does not exist.")
    product = response.json() 
    if not (product["min_loan_term"] <= application.term <= product["max_loan_term"]):
        raise HTTPException(status_code=400, detail=f'Agreement term should be between {product["min_loan_term"]} and {product["max_loan_term"]}')
    if not (product["min_interest_rate"] <= application.interest <= product["max_interest_rate"]):
        raise HTTPException(status_code=400, detail=f'Interest should be between {product["min_interest_rate"]} and {product["max_interest_rate"]}')
    
    
    # Create a pending status
    application_id = crud_applications.create_application(db, Application(
                                                    client_id=application.client_id,
                                                    product_id=application.product_id,
                                                    disbursement_amount=application.disbursment_amount,
                                                    term=application.term,
                                                    interest=application.interest,
                                                    status=enums.ApplicationStatus.PENDING.name))
    
    # Send a request to Scoring service as a background task
    background_tasks.add_task(send_application_to_scoring, db, application_id)
    return ApplicationResponse(application_id=application_id)

# Cancel an application by id
@router.post("/{application_id}/close", response_model=None, summary="Cancel the application", description="Cancels the existing application, send the cancellation request to Scoring and Product Engine services.")
async def cancel_application(application_id : int, db: Session = Depends(get_db)) -> None:
    application = crud_applications.get_application_by_id(db, application_id)
    
    if not application:
        raise HTTPException(status_code=404, detail="Application with the given ID does not exist.")
    
    if application.status == enums.ApplicationStatus.PENDING:
        # todo: request cancellation request to Scoring service
        pass
    elif application.status == enums.ApplicationStatus.CONFIRMED:
        # todo: request cancellation request to PE service
        pass
    
    crud_applications.update_status_of_application(db, application_id, enums.ApplicationStatus.CANCELLED)
    return

@router.get("/{application_id}/get", summary="Get the application", description="Fetches the application by its id from the database.")
async def get_application(application_id : int, db: Session = Depends(get_db)) -> None:
    application = crud_applications.get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application with the given ID does not exist.")

    return crud_applications.get_status_of_application_by_id(db, application_id).name