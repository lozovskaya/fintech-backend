import datetime
import re
from pydantic import BaseModel, ValidationInfo, field_validator


class AgreementModel(BaseModel):
    product_id: int
    client_id: int
    term: int
    principal : float
    interest_rate : float
    origination_amount : float
    activation_date : datetime.datetime
    status : str
    disbursement_amount : float
    
    
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

MAX_NAME_LEN = 30

class ClientModel(BaseModel):
    first_name: str
    second_name: str
    third_name: str
    birthday: str
    passport_number: str
    email: str
    phone: str
    salary: float
    
    @field_validator('first_name', 'second_name', 'third_name', 'phone', 'email', 'passport_number')
    @classmethod
    def validate_names(cls, value: str, info: ValidationInfo):
        if len(value) > MAX_NAME_LEN:
            raise ValueError(f'{info.field_name} length must be less than {MAX_NAME_LEN} symbols')
        return value
    
    @field_validator('birthday')
    @classmethod
    def validate_birthday(cls, value):
        if not re.match(r'^\d{2}.\d{2}.\d{4}$', value):
            raise ValueError('Birthday must be in the format DD.MM.YYYY')
        return value


class AgreementRequest(BaseModel):
    product_code: str
    client : ClientModel
    term: int
    interest: float
    disbursement_amount: float


class AgreementResponse(BaseModel):
    agreement_id: int
    
    
class ApplicationRequest(BaseModel):
    client_id : int
    product_id : int
    disbursement_amount: float
    term: int
    interest: float
    agreement_id: int
    
    
class KafkaProducerNewAgreementMessage(BaseModel):
    agreement_id : int
    client_id : int
    product_id : int
    disbursement_amount: float
    term: int
    interest: float

class SchedulePaymentModel(BaseModel):
    agreement_id : int
    status : str
    payment_order : int
    planned_payment_date : datetime.date
    period_start_date : datetime.date
    period_end_date : datetime.date
    principal_payment : float
    interest_payment : float

class KafkaOverduePayment(BaseModel):
    client_id : int
    agreement_id : int
    overdue_date : datetime.datetime
    payment : float