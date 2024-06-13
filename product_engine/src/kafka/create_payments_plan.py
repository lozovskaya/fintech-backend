from datetime import timedelta
import json
import logging

from models.enums import AgreementStatus, SchedulePaymentStatus, ScoringStatus
from cruds import crud_agreements, crud_schedule_payment
from dependencies import get_repo, payment_plan_helper
from models.schemas import SchedulePaymentModel
from models.models import SchedulePayment, Agreement


async def receive_scoring_result(msg):
    message = json.loads(msg.value.decode('ascii'))
    logging.info(f"Message from Kafka consumer, scoring response: {message}")
    if message["scoring_result"] == ScoringStatus.APPROVED.name:
        await create_payments_plan(int(message["agreement_id"]))


async def create_payments_plan(agreement_id: int):
    async for repository in get_repo(Agreement):
        agreement = await crud_agreements.get_agreement_by_id(repository, agreement_id)

    payment_plan = payment_plan_helper.create_payment_plan(agreement.term, agreement.activation_date, 
                                                            agreement.principal, agreement.interest_rate)
    payments = []
    for period in range(1, agreement.term + 1):
        payment_data = payment_plan[period]
        period_start_date = agreement.activation_date + timedelta(days=(period - 1) * 30)
        period_end_date = agreement.activation_date + timedelta(days=period * 30)
        payments.append(SchedulePaymentModel(agreement_id=agreement_id,
                                                status=SchedulePaymentStatus.FUTURE.name,
                                                payment_order=period,
                                                planned_payment_date=payment_data["payment_date"],
                                                period_start_date=period_start_date.date(),
                                                period_end_date=period_end_date.date(),
                                                principal_payment=round(payment_data["principal_payment"], 2),
                                                interest_payment=round(payment_data["interest_payment"], 2)))

    async for repository in get_repo(SchedulePayment):
        await crud_schedule_payment.create_payment_plan(repository, payments)
    
    async for repository in get_repo(Agreement):
        await crud_agreements.update_status_of_agreement(repository, agreement_id, AgreementStatus.ACTIVE)