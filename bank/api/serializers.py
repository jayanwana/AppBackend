from rest_framework.relations import RelatedField, ManyRelatedField
from rest_framework import serializers
from bank.models import CashCall, Refill
from rest_framework.metadata import SimpleMetadata
from django.utils.encoding import force_text
from django.utils.functional import lazy


class ChoicesMetadata(SimpleMetadata):

    def get_field_info(self, field):
        field_info = super().get_field_info(field)
        if (isinstance(field, (RelatedField, ManyRelatedField)) and
                field.field_name in getattr(field.parent.Meta, 'extra_choice_fields', [])):
            field_info['choices'] = [{
                'value': choice_value,
                'display_name': force_text(choice_name, strings_only=True)
            } for choice_value, choice_name in field.get_choices().items()]
        return field_info


class RefillSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Refill
        fields = ['url', 'id', 'amount', 'user', 'previous_balance',
                  'current_balance', 'date_deposited', 'verified']
        read_only_fields = ['id', 'user', 'previous_balance',
                            'current_balance', 'date_deposited', 'verified']


class CashCallSerializer(serializers.HyperlinkedModelSerializer, ChoicesMetadata):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    # address = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = CashCall
        fields = ['url', 'id', 'amount', 'address', 'user', 'previous_balance', 'current_balance', 'date_deposited']
        read_only_fields = ['id', 'user', 'previous_balance', 'current_balance', 'date_deposited']
        extra_choice_fields = ['address']

    # def validate(self, attrs):
    #     user = None
    #     request = self.context.get("request")
    #     if request and hasattr(request, "user"):
    #         user = request.user
    #         if user

    def validate_address(self, value):
        if value:
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                user = request.user
                address_list = user.address.all()
                if value not in address_list:
                    raise serializers.ValidationError(
                        'Address does not match User.'
                    )
        return value

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
            address = [(u.id, u.street_address) for u in obj.address.all()]
        except AttributeError:
            address = list(tuple())
        return address
