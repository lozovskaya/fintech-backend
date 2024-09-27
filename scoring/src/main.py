import time
from fastapi import BackgroundTasks, Depends, FastAPI
from cruds import crud_applications_scored 

from models.enums import ScoringStatus
from models.schemas import ApplicationRequest
from sqlalchemy.orm import Session

from dependencies import get_db
from models.models import ApplicationScored

def score_application(scoring_id, db):
    # imitate a long scoring
    time.sleep(10)
    crud_applications_scored.update_status_of_scored_application(db, scoring_id, ScoringStatus.APPROVED)
    

app = FastAPI()
application_status = {}

@app.post("/", summary="Scoring service stub")
async def receive_application_for_scoring(application: ApplicationRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    scoring_id = crud_applications_scored.create_scored_application(db, ApplicationScored(application_id=application.application_id,
                                                                             status=ScoringStatus.PENDING.name))
    
    background_tasks.add_task(score_application, scoring_id, db)
    return {"scoring_id": scoring_id}


@app.get("/get/application_id/{application_id}", summary="Scoring service stub")
async def get_scoring_id(application_id: int, db: Session = Depends(get_db)):
    return crud_applications_scored.get_scored_application_by_application_id(db, application_id)


@app.get("/get/{scoring_id}", summary="Scoring service stub")
async def get_scoring_result(scoring_id: int, db: Session = Depends(get_db)):
    return crud_applications_scored.get_scored_application_by_scoring_id(db, scoring_id)