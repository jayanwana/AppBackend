from bank.api.viewsets import RefillViewSet, CashCallViewSet
from accounts.api.viewsets import UserViewSet, UserRegistrationAPIView, UserAddressViewSet
from rest_framework import routers
from django.urls import path, include


router = routers.DefaultRouter()
router.register('refill', RefillViewSet)
router.register('cash_call', CashCallViewSet)
router.register('user', UserViewSet)
router.register('address', UserAddressViewSet)
