from typing import List
from sqlalchemy import desc 

from models.enums import ApplicationStatus
from models.models import Application
from models.schemas import ApplicationRequest
from common.repo.repository import DatabaseRepository


async def get_application_by_id(repo: DatabaseRepository, application_id: int) -> Application:
    application = await repo.filter(Application.application_id == application_id)
    if not application:
        return None
    return application[0]


async def get_all_applications(repo: DatabaseRepository) -> List[Application]:
    applications = await repo.filter()
    if not applications:
        return None
    return applications


async def get_all_applications_by_status(repo: DatabaseRepository, status: ApplicationStatus) -> List[Application]:
    applications = await repo.filter(Application.status == status.name)
    if not applications:
        return None
    return applications


async def get_all_applications_by_client(repo: DatabaseRepository, client_id: int) -> List[Application]:
    return await repo.filter(Application.client_id == client_id, order_by=desc(Application.timestamp))

async def get_status_of_application_by_id(repo: DatabaseRepository, application_id: int) -> ApplicationStatus:
    application = await repo.filter(Application.application_id == application_id)
    if application:
        return ApplicationStatus[application[0].status]
    return None

async def get_same_applications(repo: DatabaseRepository, application: ApplicationRequest) -> List[Application]:
    return await repo.filter(
        Application.client_id == application.client_id, 
        Application.product_id == application.product_id,
        Application.disbursement_amount == application.disbursement_amount,
        Application.term == application.term,
        Application.interest == application.interest
    )

async def create_application(repo: DatabaseRepository, data: dict) -> int:
    created_application = await repo.create(data)
    return created_application.application_id

async def delete_application(repo: DatabaseRepository, application_id: int) -> Application:
    application = await get_application_by_id(repo, application_id)
    if application:
        await repo.delete(Application.application_id == application_id)
        return application
    return None

async def update_status_of_application(repo: DatabaseRepository, application_id: int, new_status: ApplicationStatus):
    application = await get_application_by_id(repo, application_id)
    if application:
        await repo.update(Application.application_id == application_id, data={"status": new_status.name})
        return application
    return None