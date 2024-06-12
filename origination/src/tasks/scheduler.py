import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

from models.enums import ApplicationStatus
from clients.scoring_client import ScoringClient
from models.models import Application


from common.libs.metaclasses import SingletonMeta
from models.schemas import ApplicationKafkaRequestToScoring

logger = logging.getLogger(__name__)

class TasksScheduler(metaclass=SingletonMeta):

    def __init__(self, scoring_client : ScoringClient, get_repo, settings, kafka_producer_scoring_request):
        self.scheduler = AsyncIOScheduler()
        self.scoring_client = scoring_client
        self.get_repo = get_repo
        self.settings = settings
        self.kafka_producer_scoring_request = kafka_producer_scoring_request
    
    
    def start_scheduler(self):
        # Add regular jobs
        self.scheduler.add_job(
            self.scan_and_update_applications_job,
            trigger=IntervalTrigger(hours=2),
            next_run_time=datetime.now()
        )
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
        
        
    async def scan_and_update_applications_job(self):
        logger.info("Starting scan and update applications job.")
        async for repository in self.get_repo():
            applications_created = await repository.filter(Application.status == ApplicationStatus.CREATED.name)
            
            for application in applications_created:
                await self.kafka_producer_scoring_request.send_message(self.settings.kafka_topic_scoring_request,
                                                                ApplicationKafkaRequestToScoring(agreement_id=application.agreement_id, 
                                                                                                 client_id=application.client_id))


    async def check_scoring_status(self, application_id: int, scoring_id: int) -> bool:
        logger.info(f"Starting check_scoring_status job {application_id}.")
        response = self.scoring_client.get_scoring_status_of_application(scoring_id)
        if not response:
            return False
        if response["status"] == ApplicationStatus.APPROVED.name or response["status"] == ApplicationStatus.REJECTED.name:
            new_status = ApplicationStatus[response["status"]].name
            async for repository in self.get_repo():
                await repository.update(Application.application_id == application_id, data={"status": new_status})
            return True
        return False


    async def check_scoring_status_job(self, application_id: int, scoring_id: int):
        if await self.check_scoring_status(application_id, scoring_id):
            self.scheduler.remove_job(f"check_scoring_status_{application_id}")
