from django.conf import settings
from django.http import HttpResponseRedirect
from bank.models import Refill, CashCall
from .serializers import RefillSerializer, CashCallSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from pypaystack import Transaction


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
        return self.queryset.filter(user=self.request.user).filter(verified=True)

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            transaction = Transaction(authorization_key=settings.PAYSTACK_PUBLIC_KEY)
            amount = float(serializer.validated_data.get('amount')) * 100
            if user.paystack_authorization_code:
                response = transaction.charge(user.email, user.paystack_authorization_code, amount)
                print("with auth code\n", response)
            else:
                response = transaction.initialize(user.email, int(amount))
                url = response[3]['authorization_url']
            self.perform_create(serializer, response)
            data = serializer.data
            data['paystack_response'] = response[3]
            return Response(data=data, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer, response):
        user = self.request.user
        balance = user.user_balance.get()
        previous_balance = balance.balance
        balance.balance += serializer.validated_data.get('amount')
        current_balance = balance.balance
        reference = response[3]['reference']
        serializer.save(user=user,
                        previous_balance=previous_balance,
                        current_balance=current_balance,
                        reference=reference)


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
