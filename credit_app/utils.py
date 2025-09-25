import math
from datetime import datetime, timedelta
from .models import Loan

def calculate_emi(principal, annual_rate, tenure_months):
    
    monthly_rate = annual_rate / 12 / 100
    emi = (principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)) / (math.pow(1 + monthly_rate, tenure_months) - 1)
    return round(emi, 2)

def calculate_credit_score(customer):
    
    loans = Loan.objects.filter(customer=customer)
    
    if not loans.exists():
        return 50  
    
    total_loans = loans.count()
    total_emis_paid = sum(loan.emis_paid_on_time for loan in loans)
    total_emis_due = sum(loan.tenure for loan in loans)
    
    
    payment_history_score = min(40, (total_emis_paid / total_emis_due) * 40) if total_emis_due > 0 else 0
    

    loan_count_score = min(20, total_loans * 2)
    
    current_year_loans = loans.filter(date_of_approval__year=datetime.now().year)
    current_year_score = min(20, current_year_loans.count() * 5)
    
    total_loan_amount = sum(loan.loan_amount for loan in loans)
    volume_score = min(20, total_loan_amount / 100000)
    
    credit_score = payment_history_score + loan_count_score + current_year_score + volume_score
    
    current_loans = loans.filter(end_date__gte=datetime.now().date())
    total_current_loan_amount = sum(loan.loan_amount for loan in current_loans)
    
    if total_current_loan_amount > customer.approved_limit:
        return 0
    
    return min(100, credit_score)
