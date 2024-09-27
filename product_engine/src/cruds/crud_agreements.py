from typing import List
from pydantic import ValidationError

from models.schemas import AgreementModel
from models.models import Agreement
from models.enums import AgreementStatus
from common.repo.repository import DatabaseRepository


async def get_agreement_by_id(repo: DatabaseRepository, agreement_id: int) -> Agreement:
    agreement = await repo.filter(Agreement.agreement_id == agreement_id)
    if not agreement:
        return None
    return agreement[0]


async def get_all_agreements_by_status(repo: DatabaseRepository, status: AgreementStatus) -> List[Agreement]:
    agreements = await repo.filter(Agreement.status == status.name)
    if not agreements:
        return None
    return agreements


async def get_all_active_agreements_by_client_id(repo: DatabaseRepository, client_id: int) -> List[Agreement]:
    agreements = await repo.filter(Agreement.client_id == client_id, Agreement.status != AgreementStatus.CLOSED.name)
    if not agreements:
        return None
    return agreements

async def get_all_agreements(repo: DatabaseRepository) -> List[Agreement]:
    agreements = await repo.filter()
    if not agreements:
        return None
    return agreements


async def create_agreement(repo: DatabaseRepository, agreement: AgreementModel) -> Agreement:
    try:
        agreement_data = agreement.model_dump()
    except ValidationError:
        return None
    created_agreement = await repo.create(agreement_data)
    return created_agreement

async def delete_agreement(repo: DatabaseRepository, agreement_id: int) -> Agreement:
    agreement = await get_agreement_by_id(repo, agreement_id)
    if agreement:
        await repo.delete(Agreement.agreement_id == agreement_id)
        return agreement
    return None