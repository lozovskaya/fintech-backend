from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
import requests

from dependencies import get_repo_dep, MIN_TIME_BETWEEN_APPLICATIONS_IN_SEC, get_scoring_client, get_task_scheduler
from models.models import Application
from models import enums
from models.schemas import ApplicationRequest, ApplicationResponse, ApplicationRequestToScoring
from cruds import crud_applications
from fastapi_utils.cbv import cbv

import datetime

from clients.scoring_client import ScoringClient
from common.repo.repository import DatabaseRepository
from common.settings.urls import PRODUCT_ENGINE_URL
from tasks.scheduler import TasksScheduler

router = APIRouter(
    prefix="/application",
    tags=["application"],
)

ApplicationRepository = Annotated[
    DatabaseRepository[Application],
    Depends(get_repo_dep),
]

@cbv(router)
class ApplicationCBV:
    repo: ApplicationRepository = Depends(get_repo_dep)
    scheduler: TasksScheduler = Depends(get_task_scheduler)
    scoring_client: ScoringClient = Depends(get_scoring_client)

    async def send_application_to_scoring(self, application: Application) -> None:
        response = self.scoring_client.send_application_for_scoring(application=ApplicationRequestToScoring(application_id=application.application_id,
                                                                                                            client_id=application.client_id,
                                                                                                            product_id=application.product_id,
                                                                                                            disbursement_amount=application.disbursement_amount,
                                                                                                            term=application.term,
                                                                                                            interest=application.interest))
        if response:
            scoring_id = response["scoring_id"]
            await crud_applications.update_status_of_application(self.repo, application.application_id, enums.ApplicationStatus.PENDING)
            self.scheduler.schedule_scoring_status_check(application.application_id, scoring_id)



    async def is_same_application_in_db(self, application: ApplicationRequest) -> int:
        applications = await crud_applications.get_same_applications(self.repo, application)
        if applications:
            return applications[0].application_id
        applications = await crud_applications.get_all_applications_by_client(self.repo, client_id=application.client_id)
        if not applications:
            return None
        recent_timestamp = applications[0].timestamp
        if (datetime.datetime.now() - recent_timestamp).total_seconds() < MIN_TIME_BETWEEN_APPLICATIONS_IN_SEC:
            return applications[0].application_id
        return None


    # Create a new application
    @router.post("/", response_model=ApplicationResponse, summary="Create an application", description="Validates product data, sends an application to Scoring service.")
    async def create_application(self, application: ApplicationRequest, background_tasks: BackgroundTasks) -> ApplicationResponse:
        # Validate product data -- commented as the request should be from PR service, we assume all data was checked
        
        # response = requests.get(url = PRODUCT_ENGINE_URL + f"/product/id/{application.product_id}")
        # if response.status_code != status.HTTP_200_OK:
        #     raise HTTPException(status_code=400, detail="Product with the given ID does not exist.")
        # product = response.json() 
        # if not (product["min_loan_term"] <= application.term <= product["max_loan_term"]):
        #     raise HTTPException(status_code=400, detail=f'Agreement term should be between {product["min_loan_term"]} and {product["max_loan_term"]}')
        # if not (product["min_interest_rate"] <= application.interest <= product["max_interest_rate"]):
        #     raise HTTPException(status_code=400, detail=f'Interest should be between {product["min_interest_rate"]} and {product["max_interest_rate"]}')
        
        # Check if it's the same application that was before
        same_application_id = await self.is_same_application_in_db(application)
        if same_application_id:
            details = {
                "message": "The same application has already been received before.",
                "application_id": same_application_id,
            }
            raise HTTPException(status_code=409, detail=details)
        
        # Create a pending status
        application_id = await crud_applications.create_application(self.repo, {"client_id": application.client_id,
                                                "product_id": application.product_id,
                                                "disbursement_amount": application.disbursement_amount,
                                                "term": application.term,
                                                "interest": application.interest,
                                                "status": enums.ApplicationStatus.CREATED.name,
                                                "timestamp": datetime.datetime.now()})
        
        # Send a request to Scoring service as a background task
        application = await crud_applications.get_application_by_id(self.repo, application_id)
        background_tasks.add_task(self.send_application_to_scoring, application)
        return ApplicationResponse(application_id=application_id)

    # Cancel an application by id
    @router.post("/{application_id}/close", response_model=None, summary="Cancel the application", description="Cancels the existing application, send the cancellation request to Scoring and Product Engine services.")
    async def cancel_application(self, application_id : int) -> None:
        application = await crud_applications.get_application_by_id(self.repo, application_id)
        
        if not application:
            raise HTTPException(status_code=404, detail="Application with the given ID does not exist.")
        
        if application.status == enums.ApplicationStatus.PENDING:
            # todo: request cancellation request to Scoring service
            pass
        elif application.status == enums.ApplicationStatus.APPROVED:
            # todo: request cancellation request to PE service
            pass
        
        await crud_applications.update_status_of_application(self.repo, application_id, enums.ApplicationStatus.CANCELLED)
        return

    @router.get("/{application_id}/get", response_model=str, summary="Get the application status", description="Fetches the application status by its id from the database.")
    async def get_application(self, application_id : int) -> str:
        status = await crud_applications.get_status_of_application_by_id(self.repo, application_id)
        if not status:
            raise HTTPException(status_code=404, detail="Application with the given ID does not exist.")
        return status.name