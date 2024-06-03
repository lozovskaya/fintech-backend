from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from models.enums import AgreementStatus
from cruds import crud_agreements
from clients.origination_client import OriginationClient

from libs.metaclasses import SingletonMeta
from models.database import SessionLocal
from models.schemas import ApplicationRequest
from fastapi import status
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TasksScheduler(metaclass=SingletonMeta):

    def __init__(self, origination_client : OriginationClient):
        self.scheduler = BackgroundScheduler()
        self.origination_client = origination_client
        
        # Add regular jobs
        self.scheduler.add_job(
            self.scan_and_resend_applications_job,
            trigger=IntervalTrigger(hours=2),
            next_run_time=datetime.now()
        )
    
    
    def start_scheduler(self):
        self.scheduler.start()    
        
        
    def scan_and_resend_applications_job(self):
        logger.info("Starting scan and resend applications job.")
        with SessionLocal() as db:
            agreements_new = crud_agreements.get_all_agreements_by_status(db, AgreementStatus.NEW)
            
        for agreement in agreements_new:
            response = self.origination_client.post_application(ApplicationRequest(client_id=agreement.client_id,
                                                           product_id=agreement.product_id,
                                                           disbursment_amount=agreement.disbursment_amount,
                                                           term=agreement.term,
                                                           interest=agreement.interest_rate))
            if response and response.status_code != status.HTTP_409_CONFLICT:
                # origination service doens't have this application / agreement
                logger.info(f"Created a new application in Origination: {response['application_id']}.")