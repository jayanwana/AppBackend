from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import User, UserAddress
from django.contrib.auth.hashers import make_password

# Create your tests here.


class AccountsTests(APITestCase):

    def setUp(self):
        """
        Initialize test User and test client
        :return:
        """
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

    def auth(self, path, data=None, put=False):
        """
        Generate access token, Handle authorization and Generate response object
        :param path: API path for response object eg /api/path/
        :param data: Dict object for POST requests
        :param put: Bool. if request method is put
        :return:
        """
        response = self.client.post("/api/token/", self.post_data)
        if response.status_code != status.HTTP_200_OK:
            return response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.json()['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        if data is None:
            response = self.client.get(f'/api/{path}/')
        elif put:
            response = self.client.put(f'/api/{path}/', data)
        else:
            response = self.client.post(f'/api/{path}/', data)
        return response

    def test_create_account(self):
        """
        Ensure we can create a new user object.
        """
        url = reverse('register_user')
        data = {
            "full_name": "Test User3",
            "email": "testuser3@email.com",
            "password": "testpassword",
            "confirm_password": "testpassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.id = response.json()['id']
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(pk=self.id).full_name, "Test User3")
        self.assertEqual(User.objects.get(pk=self.id).email, "testuser3@email.com")

    def test_user_authentication(self):
        """
        Ensure user authentication works
        """
        response = self.client.post("/api/token/", self.post_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'access')
        self.assertContains(response, 'refresh')
        self.access_token = response.json()['access']

    def test_invalid_user_authentication(self):
        """
        Ensure invalid auth details are rejected
        :return:
        """
        post_data = {
            "email": "wronguser@email.com",
            "password": "wrongpassword"
        }
        response = self.client.post("/api/token/", post_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEquals(response.json(), {'detail': 'The Email and Password combination is incorrect'})

    def test_user_detail(self):
        """
        Ensure a User can access its correct details
        """
        response = self.auth('user')
        self.date_joined = response.json()["results"][0]["date_joined"]  # Timezone conversion issues require this fix
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json()['count'], 1)
        self.assertEquals(response.json()['results'],
                          [{'url': f'http://testserver/api/user/{self.user.id}/',
                            'id': self.user.id,
                            'email': self.user.email,
                            'full_name': self.user.full_name, 'user_balance': self.user.user_balance.get().balance,
                            'date_joined': self.date_joined,
                            'refill': [], 'cash_call': []}])

    def test_address_create(self):
        """
        Ensure we can add a user address
        """
        data = {
            "street_address": "test address",
            "city": "test city",
            "state": "test state",
            "country": "test country"
        }
        response = self.auth('address', data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.user_address = UserAddress.objects.get(user=self.user)
        self.assertEquals(self.user_address.street_address, 'test address')
        self.assertEquals(self.user_address.city, 'test city')
        self.assertEquals(self.user_address.state, 'test state')
        self.assertEquals(self.user_address.country, 'test country')

    def test_password_change(self):
        """
        Ensure change password works as intended
        :return:
        """
        data = {
            "old_password": 'testpassword',
            "new_password": 'newtestpassword'
        }
        response = self.auth('change_password', data, put=True)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.auth('user')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.post_data = {
            "email": "testuser@email.com",
            "password": 'newtestpassword'
        }
        response = self.auth('user')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_password_change(self):
        """
        Ensure password cannot be changed with invalid details
        :return:
        """
        data = {
            "old_password": 'wrongpassword',
            "new_password": 'newtestpassword'
        }
        response = self.auth('change_password', data, put=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(), {"old_password": ["Wrong password."]})
