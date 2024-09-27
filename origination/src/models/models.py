from sqlalchemy import Column, DateTime, Float, Integer, String


from .database import Base


class Application(Base):
    __tablename__ = 'application'

    application_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer)
    product_id = Column(Integer)
    disbursement_amount = Column(Float)
    term = Column(Integer)
    interest = Column(Float)
    status = Column(String)
    timestamp = Column(DateTime)
    agreement_id = Column(Integer)
