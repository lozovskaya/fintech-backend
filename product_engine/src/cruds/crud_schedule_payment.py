from datetime import datetime
from typing import List
from pydantic import ValidationError

from models.models import SchedulePayment
from common.repo.repository import DatabaseRepository
from models.schemas import SchedulePaymentModel
from models.enums import SchedulePaymentStatus


async def get_all_planned_payments_by_agreement_id(repo: DatabaseRepository, agreement_id: int) -> List[SchedulePayment]:
    agreement = await repo.filter(SchedulePayment.agreement_id == agreement_id)
    if not agreement:
        return None
    return agreement


async def create_payment_plan(repo: DatabaseRepository, payment_plan: List[SchedulePaymentModel]):
    payment_data = []
    for payment in payment_plan:
        try:
            payment_data.append(payment.model_dump())
        except ValidationError:
            return None
        
    for payment_data in payment_data:
        await repo.create(payment_data)

async def get_scheduled_payment_by_date(repo: DatabaseRepository, date: datetime) -> SchedulePayment:
    payments = await repo.filter(SchedulePayment.planned_payment_date >= datetime.date(date))
    if not payments:
        return None
    return payments[0]

async def get_scheduled_payment_by_id(repo: DatabaseRepository, payment_id: int) -> SchedulePayment:
    payments = await repo.filter(SchedulePayment.payment_id == payment_id)
    if not payments:
        return None
    return payments[0]

async def get_all_scheduled_payments_by_status(repo: DatabaseRepository, status: SchedulePaymentStatus) -> List[SchedulePayment]:
    payments = await repo.filter(SchedulePayment.status == status.name)
    if not payments:
        return None
    return payments
    
async def update_status_of_scheduled_payment(repo: DatabaseRepository, payment_id: int, new_status: SchedulePaymentStatus):
    payment = await get_scheduled_payment_by_id(repo, payment_id)
    if payment:
        await repo.update(SchedulePayment.payment_id == payment_id, data={"status": new_status.name})
        return payment
    return None