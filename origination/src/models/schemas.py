import datetime
from pydantic import BaseModel

class ApplicationRequest(BaseModel):
    client_id : int
    product_id : int
    disbursement_amount: float
    term: int
    interest: float
    
class ApplicationModel(BaseModel):
    client_id : int
    product_id : int
    disbursement_amount: float
    term: int
    interest : float
    status : str
    timestamp : datetime.datetime

class ApplicationResponse(BaseModel):
    application_id: int
    
    
class ApplicationRequestToScoring(BaseModel):
    application_id : int
    client_id : int
    product_id : int
    disbursement_amount: float
    term: int
    interest: float