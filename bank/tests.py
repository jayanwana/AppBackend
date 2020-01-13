from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import User, UserAddress
from django.contrib.auth.hashers import make_password

# Create your tests here.


class BankTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            full_name="Test User",
            email="testuser@email.com",
            password=make_password("testpassword"),
            )
        self.user.save()
        self.post_data = {
            "email": "testuser@email.com",
            "password": "testpassword"
        }

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
        response = self.auth('user')
        self.assertEquals(response.json()['results'][0]['user_balance'], self.user.user_balance.get().balance)

    def test_refill(self):
        amount = 5000.00
        response = self.auth('refill', data={'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertAlmostEqual(float(response.json()['amount']), amount)
        self.assertAlmostEqual(float(response.json()['current_balance']),
                               float(response.json()['previous_balance']) + amount)
        self.assertAlmostEqual(float(response.json()['current_balance']),
                               self.user.user_balance.get().balance)
        response = self.auth('refill')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json()['count'], 1)
        self.assertContains(response, 'results')
        self.assertEquals(len(response.json()['results']), 1)
        self.assertEquals(len(response.json()['results'][0]), 6)

    def test_cash_call_below_balance(self):
        amount = 5000.00
        response = self.auth('cash_call', data={'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), {'amount': ['You Can Not Withdraw More Than Your Balance.']})

    def test_cash_call(self):
        amount = 50000.00
        response = self.auth('refill', data={'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        amount = 5000.00
        response = self.auth('cash_call', data={'amount': amount})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(float(response.json()['current_balance']),
                          self.user.user_balance.get().balance)
        self.assertAlmostEqual(float(response.json()['current_balance']),
                               float(response.json()['previous_balance']) - amount)


