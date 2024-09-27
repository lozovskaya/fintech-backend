import datetime
from pydantic import BaseModel


class AgreementModel(BaseModel):
    product_id: int
    client_id: int
    term: int
    principal : float
    interest_rate : float
    origination_amount : float
    activation_date : datetime.datetime
    status : str
    
    
class ProductModel(BaseModel):
    client_friendly_name : str
    internal_code : str
    min_loan_term : int
    max_loan_term : int
    min_principal_amount : float
    max_principal_amount : float
    min_interest_rate : float
    max_interest_rate : float
    min_origination_amount : float
    max_origination_amount : float


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
    disbursment_amount: float

class AgreementResponse(BaseModel):
    agreement_id: int