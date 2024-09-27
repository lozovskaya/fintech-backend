from pydantic import BaseModel

class ClientModel(BaseModel):
    first_name: str
    second_name: str
    third_name: str
    birthday: str
    passport_number: str
    email: str
    phone: str
    salary: float

class AgreementRequest(BaseModel):
    product_code: str
    client : ClientModel
    term: int
    interest: float
    disbursement_amount: float

class ApplicationRequest(BaseModel):
    client_id : int
    product_id : int
    disbursement_amount: float
    term: int
    interest: float