from datetime import datetime
import json
import logging

from dependencies import get_repo
from models.models import Agreement
from cruds import crud_agreements, crud_schedule_payment
from models.models import SchedulePayment, Agreement
from models.enums import SchedulePaymentStatus



async def receive_new_payment(msg):
    message = json.loads(msg.value.decode('ascii'))
    logging.info(f"Message from Kafka consumer, new payment received: {message}")
    await complete_payment(int(message["agreement_id"]), datetime.fromisoformat(message["date"]), float(message["payment"]))
    

async def complete_payment(agreement_id: int, date: datetime, payment: float):
    async for repository in get_repo(Agreement):
        agreement = await crud_agreements.get_agreement_by_id(repository, agreement_id)
        
    async for repository in get_repo(SchedulePayment):
        scheduled_payment = await crud_schedule_payment.get_scheduled_payment_by_date(repository, date)
        logging.info(f"Found the nearest payment, id: {scheduled_payment.payment_id}")
        logging.info(f"Payment difference: {payment}, {scheduled_payment.principal_payment}, {scheduled_payment.interest_payment}")
        difference = payment + scheduled_payment.principal_payment + scheduled_payment.interest_payment
        logging.info(f"Payment difference: {difference}")
        if abs(difference) < 1e-9:
            await crud_schedule_payment.update_status_of_scheduled_payment(repository, scheduled_payment.payment_id, SchedulePaymentStatus.PAID)
    