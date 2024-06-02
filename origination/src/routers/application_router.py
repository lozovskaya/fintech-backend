from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
import requests

from dependencies import PRODUCT_ENGINE_URL, get_db, MIN_TIME_BETWEEN_APPLICATIONS_IN_SEC, get_scoring_client, get_task_scheduler
from models.models import Application
from models import enums
from models.schemas import ApplicationRequest, ApplicationResponse, ApplicationRequestToScoring
from sqlalchemy.orm import Session
from cruds import crud_applications

import datetime

from clients.scoring_client import ScoringClient
from tasks.scheduler import TasksScheduler

router = APIRouter(
    prefix="/application",
    tags=["application"],
)

def send_application_to_scoring(application: Application, db: Session, scoring_client: ScoringClient, scheduler: TasksScheduler):
    response = scoring_client.send_application_for_scoring(application=ApplicationRequestToScoring(application_id=application.application_id,
                                                                                                   client_id=application.client_id,
                                                                                                    product_id=application.product_id,
                                                                                                    disbursment_amount=application.disbursement_amount,
                                                                                                    term=application.term,
                                                                                                    interest=application.interest))
    if response:
        scoring_id = response["scoring_id"]
        crud_applications.update_status_of_application(db, application.application_id, enums.ApplicationStatus.PENDING)
        scheduler.schedule_scoring_status_check(application.application_id, scoring_id)

def is_same_application_in_db(db: Session, application: ApplicationRequest) -> bool:
    if crud_applications.get_same_applications(db, application):
        return True
    recent_timestamp = crud_applications.get_all_applications_by_client(db, application.client_id)
    if not recent_timestamp:
        return False
    recent_timestamp = recent_timestamp[0].timestamp
    return (datetime.datetime.now() - recent_timestamp).total_seconds() < MIN_TIME_BETWEEN_APPLICATIONS_IN_SEC


# Create a new application
@router.post("/", response_model=ApplicationResponse, summary="Create an application", description="Validates product data, sends an application to Scoring service.")
async def create_application(application: ApplicationRequest, background_tasks: BackgroundTasks, 
                             db: Session = Depends(get_db), scoring_client: ScoringClient = Depends(get_scoring_client), scheduler = Depends(get_task_scheduler)) -> ApplicationResponse:
    # Validate product data
    response = requests.get(url = PRODUCT_ENGINE_URL + f"/product/id/{application.product_id}")
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=400, detail="Product with the given ID does not exist.")
    product = response.json() 
    if not (product["min_loan_term"] <= application.term <= product["max_loan_term"]):
        raise HTTPException(status_code=400, detail=f'Agreement term should be between {product["min_loan_term"]} and {product["max_loan_term"]}')
    if not (product["min_interest_rate"] <= application.interest <= product["max_interest_rate"]):
        raise HTTPException(status_code=400, detail=f'Interest should be between {product["min_interest_rate"]} and {product["max_interest_rate"]}')
    
    # Check if it's the same application that was before
    if is_same_application_in_db(db, application):
        raise HTTPException(status_code=409, detail="The same application has already been received before.")
    
    # Create a pending status
    application_id = crud_applications.create_application(db, Application(
                                                    client_id=application.client_id,
                                                    product_id=application.product_id,
                                                    disbursement_amount=application.disbursment_amount,
                                                    term=application.term,
                                                    interest=application.interest,
                                                    status=enums.ApplicationStatus.CREATED.name,
                                                    timestamp=datetime.datetime.now()))
    
    # Send a request to Scoring service as a background task
    application = crud_applications.get_application_by_id(db, application_id)
    background_tasks.add_task(send_application_to_scoring, application, db, scoring_client, scheduler)
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
    elif application.status == enums.ApplicationStatus.APPROVED:
        # todo: request cancellation request to PE service
        pass
    
    crud_applications.update_status_of_application(db, application_id, enums.ApplicationStatus.CANCELLED)
    return

@router.get("/{application_id}/get", summary="Get the application status", description="Fetches the application status by its id from the database.")
async def get_application(application_id : int, db: Session = Depends(get_db)) -> None:
    application = crud_applications.get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application with the given ID does not exist.")

    return crud_applications.get_status_of_application_by_id(db, application_id).name