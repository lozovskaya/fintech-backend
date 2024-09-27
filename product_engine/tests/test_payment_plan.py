from datetime import datetime
import pytest, openpyxl
import pandas as pd

from src.helpers.payment_plan_creator import PaymentPlanHelper

column_names = "period principal_payment interest_payment total_payment	left".split()


def load_reference_values(file_path):
    return pd.read_excel(file_path, names=column_names, engine='openpyxl')


def compare_plans(plan, reference_plan):
    for idx, ref_row in reference_plan.iterrows():
        if idx == 0:
            continue
        calc_row = plan[idx]
        
        # Normalise values:
        calc_row['principal_payment'] = round(calc_row['principal_payment'], 2)
        calc_row['interest_payment'] = round(calc_row['interest_payment'], 2)
        ref_row['principal_payment'] = round(ref_row['principal_payment'], 2)
        ref_row['interest_payment'] = round(ref_row['interest_payment'], 2)
        ref_row['total_payment'] = round(ref_row['total_payment'], 2)
        
        assert calc_row['principal_payment'] == ref_row['principal_payment']
        assert calc_row['interest_payment'] == ref_row['interest_payment']
        

def test_plan_case1():
    helper = PaymentPlanHelper()
    loan_principal_amount = 1000000
    annual_interest_rate = 12
    term_months = 24
    activation_date = datetime(2024, 1, 1)
    
    plan = helper.create_payment_plan(term_months, activation_date, loan_principal_amount, annual_interest_rate)
    reference_plan = load_reference_values("./reference/test_plan_case1.xlsx")
    
    assert len(plan) == 24
    compare_plans(plan, reference_plan)
    

def test_plan_case2():
    helper = PaymentPlanHelper()
    loan_principal_amount = 10000
    annual_interest_rate = 90
    term_months = 8
    activation_date = datetime(2024, 1, 1)
    
    plan = helper.create_payment_plan(term_months, activation_date, loan_principal_amount, annual_interest_rate)
    reference_plan = load_reference_values("./reference/test_plan_case2.xlsx")
    
    assert len(plan) == 8
    compare_plans(plan, reference_plan)


def test_plan_case3():
    helper = PaymentPlanHelper()
    loan_principal_amount = 500000
    annual_interest_rate = 22
    term_months = 36
    activation_date = datetime(2024, 1, 1)
    
    plan = helper.create_payment_plan(term_months, activation_date, loan_principal_amount, annual_interest_rate)
    reference_plan = load_reference_values("./reference/test_plan_case3.xlsx")
    
    assert len(plan) == 36
    compare_plans(plan, reference_plan)
