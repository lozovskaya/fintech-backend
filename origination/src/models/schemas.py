from pydantic import BaseModel

class ApplicationRequest(BaseModel):
    client_id : int
    product_id : int
    disbursment_amount: float
    term: int
    interest: float

class ApplicationResponse(BaseModel):
    application_id: int
    
