from sqlalchemy import Column, Float, Integer, String


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
