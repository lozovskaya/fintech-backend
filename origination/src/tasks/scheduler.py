from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from models.enums import ApplicationStatus
from cruds import crud_applications
from clients.scoring_client import ScoringClient

from libs.metaclasses import SingletonMeta
from models import enums
from models.database import SessionLocal
from models.schemas import ApplicationRequestToScoring


class TasksScheduler(metaclass=SingletonMeta):

    def __init__(self, scoring_client : ScoringClient):
        self.scheduler = BackgroundScheduler()
        self.scoring_client = scoring_client
        
        # Add regular jobs
        self.scheduler.add_job(
            self.scan_and_update_applications_job,
            args=[scoring_client],
            trigger=IntervalTrigger(hours=2),
            next_run_time=datetime.now()
        )
    
    
    def start_scheduler(self):
        self.scheduler.start()    
        
    def schedule_scoring_status_check(self, application_id: int, scoring_id: int):
        self.scheduler.add_job(
            self.check_scoring_status_job,
            args=[application_id, scoring_id],
            id=f"check_scoring_status_{application_id}",
            trigger=IntervalTrigger(seconds=10),
            next_run_time=datetime.now(),
            replace_existing=True
        )
        
        
    def scan_and_update_applications_job(self, scoring_client : ScoringClient):
        with SessionLocal() as db:
            applications_created = crud_applications.get_all_applications_by_status(db, ApplicationStatus.CREATED)
            applications_pending = crud_applications.get_all_applications_by_status(db, ApplicationStatus.PENDING)
            
        for application in applications_pending:
            if not self.scheduler.get_job(f"check_scoring_status_{application.application_id}"):
                response = scoring_client.get_scoring_id_of_application(application.application_id)
                if response:
                    scoring_id = response["scoring_id"]
                    self.schedule_scoring_status_check(application.application_id, scoring_id)
                
        for application in applications_created:
            response = scoring_client.send_application_for_scoring(application=ApplicationRequestToScoring(application_id=application.application_id,
                                                                                                            client_id=application.client_id,
                                                                                                            product_id=application.product_id,
                                                                                                            disbursment_amount=application.disbursement_amount,
                                                                                                            term=application.term,
                                                                                                            interest=application.interest))
            if response:
                scoring_id = response["scoring_id"]
                with SessionLocal() as db:
                    crud_applications.update_status_of_application(db, application.application_id, enums.ApplicationStatus.PENDING)
                self.schedule_scoring_status_check(application.application_id, scoring_id)


    def check_scoring_status(self, application_id: int, scoring_id: int) -> bool:
        response = self.scoring_client.get_scoring_status_of_application(scoring_id)
        if not response:
            return False
        if response["status"] == ApplicationStatus.APPROVED.name or response["status"] == ApplicationStatus.REJECTED.name:
            new_status = ApplicationStatus[response["status"]]
            with SessionLocal() as db:
                crud_applications.update_status_of_application(db, application_id, new_status)
            return True
        return False


    def check_scoring_status_job(self, application_id: int, scoring_id: int):
        if self.check_scoring_status(application_id, scoring_id):
            self.scheduler.remove_job(f"check_scoring_status_{application_id}")
