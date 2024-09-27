from pydantic import BaseModel


class ApplicationRequest(BaseModel):
    application_id : int
    client_id : int
    product_id : int
    disbursement_amount: float
    term: int
    interest: float