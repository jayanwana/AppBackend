from rest_framework import serializers
from bank.models import CashCall, Refill


class RefillSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Refill
        fields = ['url', 'id', 'amount', 'user', 'previous_balance', 'current_balance', 'date_deposited']
        read_only_fields = ['id', 'user', 'previous_balance', 'current_balance', 'date_deposited']


class CashCallSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    address = serializers.SerializerMethodField('get_user_address')

    class Meta:
        model = CashCall
        fields = ['url', 'id', 'amount', 'address', 'user', 'previous_balance', 'current_balance', 'date_deposited']
        read_only_fields = ['id', 'user', 'previous_balance', 'current_balance', 'date_deposited']

    def validate_amount(self, value):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        balance = user.user_balance.get()

        if balance.balance < value:
            raise serializers.ValidationError(
                'You Can Not Withdraw More Than Your Balance.'
            )
        return value

    def get_user_address(self, obj):
        try:
            address = obj.address.get().street_address
        except AttributeError:
            return None
        return address
