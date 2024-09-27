from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from models.enums import AgreementStatus
from cruds import crud_agreements
from clients.origination_client import OriginationClient

from common.libs.metaclasses import SingletonMeta
from models.schemas import ApplicationRequest
from fastapi import status
import logging

from models.models import Agreement

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TasksScheduler(metaclass=SingletonMeta):

    def __init__(self, origination_client : OriginationClient, get_repo):
        self.scheduler = AsyncIOScheduler()
        self.origination_client = origination_client
        self.get_repo = get_repo
        
        # Add regular jobs
        self.scheduler.add_job(
            self.scan_and_resend_applications_job,
            trigger=IntervalTrigger(hours=2),
            next_run_time=datetime.now()
        )
    
    
    def start_scheduler(self):
        self.scheduler.start()    
        
        
    async def scan_and_resend_applications_job(self):
        logger.info("Starting scan and resend applications job.")
        async for repository in self.get_repo(Agreement):
            agreements_new = await crud_agreements.get_all_agreements_by_status(repository, AgreementStatus.NEW)
            if agreements_new:
                for agreement in agreements_new:
                    response = self.origination_client.post_application(ApplicationRequest(client_id=agreement.client_id,
                                                                product_id=agreement.product_id,
                                                                disbursement_amount=agreement.disbursement_amount,
                                                                term=agreement.term,
                                                                interest=agreement.interest_rate))
                    if response and response.status_code != status.HTTP_409_CONFLICT:
                        # origination service doens't have this application / agreement
                        logger.info(f"Created a new application in Origination: {response['application_id']}.")