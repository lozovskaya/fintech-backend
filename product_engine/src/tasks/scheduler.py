from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import date, datetime

from models.enums import AgreementStatus, SchedulePaymentStatus
from cruds import crud_agreements, crud_schedule_payment
from clients.origination_client import OriginationClient

from common.libs.metaclasses import SingletonMeta
from models.schemas import ApplicationRequest, KafkaOverduePayment
from fastapi import status
import logging

from models.models import Agreement, SchedulePayment

logger = logging.getLogger(__name__)

class TasksScheduler(metaclass=SingletonMeta):

    def __init__(self, origination_client : OriginationClient, get_repo, kafka_producer, kafka_topic_overdue_payment):
        self.scheduler = AsyncIOScheduler()
        self.origination_client = origination_client
        self.get_repo = get_repo
        self.kafka_producer = kafka_producer
        self.kafka_topic_overdue_payment = kafka_topic_overdue_payment
        
        # Add regular jobs
        self.scheduler.add_job(
            self.scan_and_resend_applications_job,
            trigger=IntervalTrigger(hours=2),
            next_run_time=datetime.now()
        )
        self.scheduler.add_job(
            self.find_overdue_payments_job,
            trigger=IntervalTrigger(hours=24),
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
                                                                interest=agreement.interest_rate, 
                                                                agreement_id=agreement.agreement_id))
                    if response and response.status_code != status.HTTP_409_CONFLICT:
                        # origination service doens't have this application / agreement
                        logger.info(f"Created a new application in Origination: {response['application_id']}.")
    
    async def find_overdue_payments_job(self):
        logger.info("Starting finding overdue payments job.")
        # today_date = datetime.now()
        today_date = datetime.strptime("2024-12-24", '%Y-%m-%d')
        async for repository in self.get_repo(SchedulePayment):
            payments = await crud_schedule_payment.get_all_scheduled_payments_by_status(repository, SchedulePaymentStatus.FUTURE)
            if payments:
                for payment in payments:
                    if payment.planned_payment_date < datetime.date(today_date):
                        async for repo in self.get_repo(Agreement):
                             client_id = await crud_agreements.get_agreement_by_id(repo, payment.agreement_id)
                             client_id = client_id.client_id
                        await self.kafka_producer.send_message(self.kafka_topic_overdue_payment, 
                                                         KafkaOverduePayment(client_id=client_id,
                                                                             agreement_id=payment.agreement_id,
                                                                             overdue_date=today_date.isoformat(),
                                                                             payment=abs(payment.principal_payment + payment.interest_payment)))
                        
                        await crud_schedule_payment.update_status_of_scheduled_payment(repository, payment.payment_id, SchedulePaymentStatus.OVERDUE)