from models.enums import ScoringStatus
from models.models import ApplicationScored
from common.repo.repository import DatabaseRepository


async def get_scored_application_by_application_id(repo: DatabaseRepository, application_id: int) -> ApplicationScored:
    scored_applications = await repo.filter(ApplicationScored.application_id == application_id)
    return scored_applications[0] if scored_applications else None

async def get_scored_application_by_scoring_id(repo: DatabaseRepository, scoring_id: int) -> ApplicationScored:
    scored_applications = await repo.filter(ApplicationScored.scoring_id == scoring_id)
    return scored_applications[0] if scored_applications else None

async def get_scored_status_of_application_by_application_id(repo: DatabaseRepository, application_id: int) -> ScoringStatus:
    scored_application = await get_scored_application_by_application_id(repo, application_id)
    if scored_application:
        return ScoringStatus[scored_application.status]
    return None

async def get_scored_status_of_application_by_scoring_id(repo: DatabaseRepository, scoring_id: int) -> ScoringStatus:
    scored_application = await get_scored_application_by_scoring_id(repo, scoring_id)
    if scored_application:
        return ScoringStatus[scored_application.status]
    return None


async def create_scored_application(repo: DatabaseRepository, data: dict) -> int:
    created_scored_application = await repo.create(data)
    return created_scored_application.scoring_id


async def delete_scored_application(repo: DatabaseRepository, scoring_id: int) -> ApplicationScored:
    scored_application = await get_scored_application_by_scoring_id(repo, scoring_id)
    if scored_application:
        await repo.delete(ApplicationScored.scoring_id == scoring_id)
        return scored_application
    return None


async def update_status_of_scored_application(repo: DatabaseRepository, scoring_id: int, new_status: ScoringStatus):
    scored_application = await get_scored_application_by_scoring_id(repo, scoring_id)
    if scored_application:
        await repo.update(ApplicationScored.scoring_id == scoring_id, data={"status": new_status.name})
        return scored_application
    return None