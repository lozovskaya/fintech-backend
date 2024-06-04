import time
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends

from dependencies import get_repo_dep
from models.models import ApplicationScored
from models import enums
from models.schemas import ApplicationRequest
from cruds import crud_applications_scored
from fastapi_utils.cbv import cbv
from common.repo.repository import DatabaseRepository

router = APIRouter(
    prefix="/scoring",
    tags=["scoring"],
)

ApplicationScoredRepository = Annotated[
    DatabaseRepository[ApplicationScored],
    Depends(get_repo_dep),
]

@cbv(router)
class ApplicationScoredCBV:
    repo: ApplicationScoredRepository = Depends(get_repo_dep)
    
    async def score_application(self, scoring_id):
        # imitate a long scoring
        time.sleep(10)
        await crud_applications_scored.update_status_of_scored_application(self.repo, scoring_id, enums.ScoringStatus.APPROVED)
        
   
    @router.post("/", summary="Scoring service stub")
    async def receive_application_for_scoring(self, application: ApplicationRequest, background_tasks: BackgroundTasks):
        scoring_id = await crud_applications_scored.create_scored_application(self.repo, {"application_id": application.application_id,
                                                                                          "status": enums.ScoringStatus.PENDING.name})
        
        background_tasks.add_task(self.score_application, scoring_id)
        return {"scoring_id": scoring_id}


    @router.get("/get/application_id/{application_id}", summary="Scoring service stub")
    async def get_scoring_id(self, application_id: int):
        return await crud_applications_scored.get_scored_application_by_application_id(self.repo, application_id)


    @router.get("/get/{scoring_id}", summary="Scoring service stub")
    async def get_scoring_result(self, scoring_id: int):
        return await crud_applications_scored.get_scored_application_by_scoring_id(self.repo, scoring_id)