from bank.api.viewsets import RefillViewSet, CashCallViewSet
from accounts.api.viewsets import UserViewSet, UserRegistrationAPIView, UserAddressViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register('refill', RefillViewSet, 'refill')
router.register('cash_call', CashCallViewSet)
router.register('user', UserViewSet)
router.register('address', UserAddressViewSet)
