from datetime import datetime, timedelta
from typing import Dict
import numpy_financial as npf

class PaymentPlanHelper:
    def __init__(self):
        pass
    
    def create_payment_plan(self, term: int, activation_date: datetime, principal: float, interest_rate: int) -> Dict[int, Dict[str, float]]:
        payment_plan = {}
        
        monthly_payment = self.calculate_pmt(principal, interest_rate, term)
        
        for period in range(1, term + 1):
            payment_date = activation_date + timedelta(days=period * 30)
            principal_payment = self.calculate_principal_payment(principal, interest_rate, term, period)
            interest_payment = self.calculate_interest_payment(principal, interest_rate, term, period)
            assert abs((principal_payment + interest_payment) - monthly_payment) < 1e-9
            payment_plan[period] = {"payment_date": payment_date.date(),
                                    "principal_payment": principal_payment,
                                    "interest_payment": interest_payment}
        
        return payment_plan
    
    
    def calculate_pmt(self, principal, annual_rate, periods) -> float:
        annual_rate /= 100
        monthly_rate = annual_rate / 12
        return float(npf.pmt(monthly_rate, periods, principal))
    

    def calculate_principal_payment(self, principal, annual_rate, periods, period) -> float:
        annual_rate /= 100
        monthly_rate = annual_rate / 12
        return float(npf.ppmt(monthly_rate, period, periods, principal))


    def calculate_interest_payment(self, principal, annual_rate, periods, period) -> float:
        annual_rate /= 100
        monthly_rate = annual_rate / 12
        return float(npf.ipmt(monthly_rate, period, periods, principal))