from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Customer, Loan
from .serializers import *
from .utils import calculate_emi, calculate_credit_score

@api_view(['POST'])
def register_customer(request):
    try:
        serializer = RegisterCustomerSerializer(data=request.data)
        if serializer.is_valid():
           
            monthly_income = serializer.validated_data['monthly_income']
            approved_limit = round((monthly_income * 36) / 100000) * 100000
            
            customer = Customer.objects.create(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                age=serializer.validated_data['age'],
                phone_number=serializer.validated_data['phone_number'],
                monthly_salary=monthly_income,
                approved_limit=approved_limit
            )
            
            response_data = {
                'customer_id': customer.customer_id,
                'name': f"{customer.first_name} {customer.last_name}",
                'age': customer.age,
                'monthly_income': customer.monthly_salary,
                'approved_limit': customer.approved_limit,
                'phone_number': customer.phone_number
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def check_eligibility(request):
    try:
        serializer = CheckEligibilitySerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            loan_amount = serializer.validated_data['loan_amount']
            interest_rate = serializer.validated_data['interest_rate']
            tenure = serializer.validated_data['tenure']
            
            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
            
            #credit score
            credit_score = calculate_credit_score(customer)
            
          
            current_loans = Loan.objects.filter(customer=customer, end_date__gte=timezone.now().date())
            total_current_emi = sum(loan.monthly_payment for loan in current_loans)
            
            if total_current_emi > (customer.monthly_salary * 0.5):
                approval = False
                corrected_interest_rate = interest_rate
            else:
                # Check approval based on credit score
                if credit_score > 50:
                    approval = True
                    corrected_interest_rate = interest_rate
                elif 30 < credit_score <= 50:
                    approval = interest_rate >= 12
                    corrected_interest_rate = max(interest_rate, 12)
                elif 10 < credit_score <= 30:
                    approval = interest_rate >= 16
                    corrected_interest_rate = max(interest_rate, 16)
                else:
                    approval = False
                    corrected_interest_rate = interest_rate
            
            monthly_installment = calculate_emi(loan_amount, corrected_interest_rate, tenure) if approval else 0
            
            response_data = {
                'customer_id': customer_id,
                'approval': approval,
                'interest_rate': interest_rate,
                'corrected_interest_rate': corrected_interest_rate,
                'tenure': tenure,
                'monthly_installment': monthly_installment
            }
            
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_loan(request):
    try:
        serializer = CreateLoanSerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            loan_amount = serializer.validated_data['loan_amount']
            interest_rate = serializer.validated_data['interest_rate']
            tenure = serializer.validated_data['tenure']
            
            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check eligibility
            credit_score = calculate_credit_score(customer)
            current_loans = Loan.objects.filter(customer=customer, end_date__gte=timezone.now().date())
            total_current_emi = sum(loan.monthly_payment for loan in current_loans)
            
            # Approval logic
            if total_current_emi > (customer.monthly_salary * 0.5):
                approval = False
                message = "Total current EMIs exceed 50% of monthly salary"
            elif credit_score > 50:
                approval = True
                message = "Loan approved"
            elif 30 < credit_score <= 50:
                approval = interest_rate >= 12
                message = "Loan approved" if approval else "Interest rate too low for credit score"
            elif 10 < credit_score <= 30:
                approval = interest_rate >= 16
                message = "Loan approved" if approval else "Interest rate too low for credit score"
            else:
                approval = False
                message = "Credit score too low"
            
            if approval:
                corrected_interest_rate = interest_rate
                if 30 < credit_score <= 50:
                    corrected_interest_rate = max(interest_rate, 12)
                elif 10 < credit_score <= 30:
                    corrected_interest_rate = max(interest_rate, 16)
                
                monthly_installment = calculate_emi(loan_amount, corrected_interest_rate, tenure)
                start_date = timezone.now().date()
                end_date = start_date + timedelta(days=tenure*30)  # Approximate month as 30 days
                
                loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=loan_amount,
                    tenure=tenure,
                    interest_rate=corrected_interest_rate,
                    monthly_payment=monthly_installment,
                    start_date=start_date,
                    end_date=end_date,
                    date_of_approval=start_date
                )
                
                response_data = {
                    'loan_id': loan.loan_id,
                    'customer_id': customer_id,
                    'loan_approved': True,
                    'message': message,
                    'monthly_installment': monthly_installment
                }
            else:
                response_data = {
                    'loan_id': None,
                    'customer_id': customer_id,
                    'loan_approved': False,
                    'message': message,
                    'monthly_installment': 0
                }
            
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        customer = loan.customer
        
        customer_data = {
            'id': customer.customer_id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'phone_number': customer.phone_number,
            'age': customer.age
        }
        
        response_data = {
            'loan_id': loan.loan_id,
            'customer': customer_data,
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_payment,
            'tenure': loan.tenure
        }
        
        return Response(response_data)
    except Loan.DoesNotExist:
        return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer)
        
        loans_data = []
        for loan in loans:
            repayments_left = loan.tenure - loan.emis_paid_on_time
            loans_data.append({
                'loan_id': loan.loan_id,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_payment,
                'repayments_left': max(0, repayments_left)
            })
        
        return Response(loans_data)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)