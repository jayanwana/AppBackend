from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from accounts.models import User, UserAddress, UserBalance
from django.contrib.auth.hashers import make_password
from .signals import deposit_verify_thread
from .models import Refill
import decimal

# Create your tests here.


class BankTests(APITestCase):

    def setUp(self):
        """
        Set up test User and Client
        :return:
        """
        self.client = APIClient()
        self.user = User.objects.create(
            full_name="Test User",
            email="testuser@email.com",
            password=make_password("testpassword"),
            paystack_authorization_code="AUTH_cie68xpqq4",
            )
        self.user.save()
        self.address = UserAddress.objects.create(
            user=self.user,
            street_address="test address",
            city="test city",
            state="test state",
            country="test country"
            )
        self.address.save()
        self.post_data = {
            "email": "testuser@email.com",
            "password": "testpassword"
        }
        deposit = 50000.00
        balance = self.user.user_balance.get()
        balance.balance = balance.balance + decimal.Decimal(deposit)
        balance.save()

    def auth(self, path, data=None):
        """
        Generate access token, Handle authorization and Generate response object
        :param path: API path for response object eg /api/path/
        :param data: Dict object for POST requests
        :return:
        """
        response = self.client.post("/api/token/", self.post_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        if data is None:
            response = self.client.get(f'/api/{path}/')
        else:
            response = self.client.post(f'/api/{path}/', data)
        return response

    def test_balance(self):
        """Ensure User Balance is correct"""
        response = self.auth('user')
        self.assertEquals(response.json()['results'][0]['user_balance'],
                          self.user.user_balance.get().balance)

    def test_refill(self):
        """
        Ensure deposits work as intended
        :return:
        """
        amount = 5000.00
        response = self.auth('refill', data={'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertAlmostEqual(float(response.json()['amount']), amount)
        self.assertAlmostEqual(float(response.json()['current_balance']),
                               float(response.json()['previous_balance']) + amount)
        self.assertEquals(response.json()['verified'], False)
        self.assertNotEqual(decimal.Decimal(response.json()['current_balance']),
                            self.user.user_balance.get().balance)
        refill = Refill.objects.get(pk=response.json()['id'])
        verify = deposit_verify_thread(refill, test=True)

        print(response.json()['paystack_response'])
        response = self.auth('refill')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json()['count'], 1)
        self.assertContains(response, 'results')
        self.assertEquals(len(response.json()['results']), 1)
        self.assertEquals(len(response.json()['results'][0]), 7)

    def test_cash_call_below_balance(self):
        """
        Ensure User cannot withdraw more than their available balance
        :return:
        """
        amount = 500000.00
        response = self.auth('cash_call', data={'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(),
                             {'amount': ['You Can Not Withdraw More Than Your Balance.']})

    def test_cash_call(self):
        """
        Ensure withdrawal works as intended
        :return:
        """
        amount = 5000.00
        response = self.auth('cash_call', data={'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(float(response.json()['current_balance']),
                          self.user.user_balance.get().balance)
        self.assertAlmostEqual(float(response.json()['current_balance']),
                               float(response.json()['previous_balance']) - amount)

    def test_cash_call_with_address(self):
        """
                Ensure withdrawal works as intended
                :return:
                """
        amount = 50000.00
        response = self.auth('refill', data={'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        amount = 5000.00
        response = self.auth('cash_call',
                             data={
                                 'amount': amount,
                                 'address': f'http://testserver/api/address/{self.user.address.get().pk}/'
                             })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(float(response.json()['current_balance']),
                          self.user.user_balance.get().balance)
        self.assertAlmostEqual(float(response.json()['current_balance']),
                               float(response.json()['previous_balance']) - amount)
        response = self.auth('cash_call')
        self.assertEquals(response.json()['results'][0]['address'],
                          f'http://testserver/api/address/{self.user.address.get().pk}/')
