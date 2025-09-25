from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Customer

class RegistrationAPITest(APITestCase):

    def test_register_customer_success(self):
        """
        Ensure we can create a new customer object successfully.
        """
  
        url = reverse('register') 
        
        data = {
            "first_name": "Test",
            "last_name": "User",
            "age": 30,
            "monthly_income": 50000,
            "phone_number": 9876543210
        }
        
   
        response = self.client.post(url, data, format='json')
        
       
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
       
        self.assertEqual(Customer.objects.count(), 1)
        
        
        customer = Customer.objects.get()
        self.assertEqual(customer.first_name, "Test")
        
    
        self.assertEqual(response.data['approved_limit'], 1800000)

    def test_register_customer_failure_missing_field(self):
        """
        Ensure API returns an error if a required field is missing.
        """
        url = reverse('register')
        data = {
            "last_name": "User", # Missing first_name
            "age": 30,
            "monthly_income": 50000,
            "phone_number": 9876543210
        }
        response = self.client.post(url, data, format='json')
        
       
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
