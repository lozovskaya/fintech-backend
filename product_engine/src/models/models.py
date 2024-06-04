from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


from .database import Base


class Product(Base):
    __tablename__ = 'product'

    product_id = Column(Integer, primary_key=True, index=True)
    client_friendly_name = Column(String)
    internal_code = Column(String, unique=True)
    min_loan_term = Column(Integer)
    max_loan_term = Column(Integer)
    min_principal_amount = Column(Float)
    max_principal_amount = Column(Float)
    min_interest_rate = Column(Float)
    max_interest_rate = Column(Float)
    min_origination_amount = Column(Float)
    max_origination_amount = Column(Float)
    
    agreement = relationship("Agreement", back_populates="product")

class Client(Base):
    __tablename__ = 'client'

    client_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    birthday = Column(DateTime)
    email = Column(String)
    phone_number = Column(String)
    passport = Column(String)
    monthly_income = Column(Float)

    agreement = relationship("Agreement", back_populates="client")

class Agreement(Base):
    __tablename__ = 'agreement'

    agreement_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('product.product_id'))
    client_id = Column(Integer, ForeignKey('client.client_id'), index=True)
    term = Column(Integer)
    principal = Column(Float)
    interest_rate = Column(Float)
    origination_amount = Column(Float)
    activation_date = Column(DateTime, index=True)
    status = Column(String)
    disbursement_amount = Column(Float)

    product = relationship("Product", back_populates="agreement")
    client = relationship("Client", back_populates="agreement")
    schedule_payments = relationship("SchedulePayment", back_populates="agreement")


class SchedulePayment(Base):
    __tablename__ = 'schedule_payment'

    payment_id = Column(Integer, primary_key=True, index=True)
    agreement_id = Column(Integer, ForeignKey('agreement.agreement_id'), index=True)
    planned_payment_date = Column(Date, index=True)
    period_start_date = Column(Date)
    period_end_date = Column(Date)
    principal_payment = Column(Float)
    interest_payment = Column(Float)
    payment_order = Column(Integer)
    status = Column(String)

    agreement = relationship("Agreement", back_populates="schedule_payments")