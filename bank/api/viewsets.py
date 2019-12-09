from bank.models import Refill, CashCall
from .serializers import RefillSerializer, CashCallSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class RefillViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return the given deposit

    list:
        Return a list of all users deposits.

    create:
        Make a new deposit.
        """
    queryset = Refill.objects.all()
    serializer_class = RefillSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'head']

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class CashCallViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return the given withdrawal.

    list:
        Return a list of all the users withdrawals.

    create:
        Make a new withdrawal.

    """
    queryset = CashCall.objects.all()
    serializer_class = CashCallSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'head']

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set
