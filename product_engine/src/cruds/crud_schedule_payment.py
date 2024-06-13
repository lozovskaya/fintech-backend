from typing import List
from pydantic import ValidationError

from models.models import SchedulePayment
from common.repo.repository import DatabaseRepository
from models.schemas import SchedulePaymentModel


async def get_all_planned_payments_by_agreement_id(repo: DatabaseRepository, agreement_id: int) -> SchedulePayment:
    agreement = await repo.filter(SchedulePayment.agreement_id == agreement_id)
    if not agreement:
        return None
    return agreement[0]


async def create_payment_plan(repo: DatabaseRepository, payment_plan: List[SchedulePaymentModel]):
    payment_data = []
    for payment in payment_plan:
        try:
            payment_data.append(payment.model_dump())
        except ValidationError:
            return None
        
    for payment_data in payment_data:
        await repo.create(payment_data)

