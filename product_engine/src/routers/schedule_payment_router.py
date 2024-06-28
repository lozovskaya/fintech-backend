from typing import Annotated, List
from fastapi import Depends, APIRouter, HTTPException
from fastapi_utils.cbv import cbv

from dependencies import get_repo_dep
from cruds import crud_schedule_payment
from models.schemas import SchedulePaymentModel


from common.repo.repository import DatabaseRepository
from models.models import SchedulePayment

router = APIRouter(
    prefix="/schedule_payment",
    tags=["schedule_payment"],)

SchedulePaymentRepository = Annotated[
    DatabaseRepository[SchedulePayment],
    Depends(get_repo_dep(SchedulePayment)),
]

@cbv(router)
class SchedulePaymentCBV:
    repo: SchedulePaymentRepository = Depends(get_repo_dep(SchedulePayment))
    
    # Get the payment plan by agreement id
    @router.get("/{agreement_id}", response_model=list[SchedulePaymentModel], summary="Get the payment plan by agreement id", description="Fetches a payment plan from the database.")
    async def get_payment_plan(self, agreement_id: int) -> List[SchedulePaymentModel]:
        plan = await crud_schedule_payment.get_all_planned_payments_by_agreement_id(self.repo, agreement_id)
        
        for i in range(len(plan)):
            plan[i] = SchedulePaymentModel(
                                            agreement_id=plan[i].agreement_id,
                                            status=plan[i].status,
                                            payment_order=plan[i].payment_order,
                                            planned_payment_date=plan[i].planned_payment_date,
                                            period_start_date=plan[i].period_start_date,
                                            period_end_date=plan[i].period_end_date,
                                            principal_payment=plan[i].principal_payment,
                                            interest_payment=plan[i].interest_payment
                                            )
        return plan
