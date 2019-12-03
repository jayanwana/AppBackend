from bank.models import Refill, CashCall
from .serializers import RefillSerializer, CashCallSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class RefillViewSet(viewsets.ModelViewSet):
    queryset = Refill.objects.all()
    serializer_class = RefillSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'head']

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set


class CashCallViewSet(viewsets.ModelViewSet):
    queryset = CashCall.objects.all()
    serializer_class = CashCallSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'head']

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set
