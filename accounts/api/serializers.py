from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from accounts.models import User, UserBalance, UserAddress
import re


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    User Registration Form. Creates new instances of the User model
    """
    email = serializers.EmailField(required=True,
                                   help_text='User Email Address. Required in email format',
                                   validators=[UniqueValidator(
                                       queryset=User.objects.all(),
                                       message="An account with this email already exists"
                                   )])
    phone_number = serializers.CharField(required=True,
                                         help_text='Mobile phone number in the Format: 08123456789',
                                         max_length=11, min_length=11,
                                         validators=[UniqueValidator(
                                             queryset=User.objects.all(),
                                             message="An account with this mobile number already exists"
                                                                     )])
    full_name = serializers.CharField(max_length=64, required=True,
                                      help_text='Full name of the User',)
    password = serializers.CharField(min_length=8, max_length=100, required=True,
                                     write_only=True,
                                     help_text='User Password, must be at least 8characters',
                                     style={'input_type': 'password'})
    confirm_password = serializers.CharField(min_length=8, max_length=100, required=True,
                                             help_text='Re-enter password for confirmation',
                                             write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ("id", "full_name", "email", "phone_number",
                  "password", "confirm_password", "date_joined")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].error_messages['required'] = \
            'Email is required'
        self.fields['email'].error_messages['blank'] = \
            'Email cannot be blank'
        self.fields['email'].error_messages['unique'] = \
            'A User with this email address already exists'
        self.fields['full_name'].error_messages['required'] = \
            'Full name is required'
        self.fields['full_name'].error_messages['blank'] = \
            'Full name cannot be blank'
        self.fields['password'].error_messages['required'] = \
            'Password is required'
        self.fields["password"].error_messages["min_length"] = \
            "password must be at least 8 characters"
        self.fields['phone_number'].error_messages['required'] = \
            'A mobile number is required'
        self.fields['phone_number'].error_messages['blank'] = \
            'Phone number cannot be blank'
        self.fields['phone_number'].error_messages['unique'] = \
            'A User with this Mobile number address already exists'
        self.fields["phone_number"].error_messages["min_length"] = \
            "Phone number must have 11 Digits"
        self.fields["phone_number"].error_messages["max_length"] = \
            "Phone number must have 11 Digits"

    def create(self, validated_data):
        """
        Create an instance of the user model
        :param validated_data:
        :return:
        """
        user = User.objects.create(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            phone_number=validated_data['phone_number'],
            password=make_password(validated_data['password']))
        return user

    def validate(self, attrs):
        """ Make sure Passwords match"""
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Those passwords don't match.")
        return attrs

    @staticmethod
    def validate_full_name(value):
        """ Ensure Full Name contains at least name and surname"""
        value_list = value.split()
        if len(value_list) < 2:
            raise serializers.ValidationError(
                'You must enter your Surname and Name.'
            )
        return value

    def validate_phone_number(self, value):
        """ Ensure it is a Nigerian Number"""
        if re.search(r'^s*[0][7-9]\d{9,11}$', str(value)):
            return value
        raise serializers.ValidationError(
            'Phone number must start with 07, 08 or 09.'
        )


class UserBalanceSerializer(serializers.ModelSerializer):
    """
    User Wallet
    """
    queryset = UserBalance.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set

    class Meta:
        model = UserBalance
        fields = ['balance']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializes thr User model and generates a url for each user
    """
    user_balance = serializers.SerializerMethodField('get_user_balance',
                                                     help_text='Balance of the Users Wallet')
    refill = serializers.HyperlinkedRelatedField(many=True, read_only=True,
                                                 help_text='URL list of Deposits bys user',
                                                 view_name='refill-detail')
    cash_call = serializers.HyperlinkedRelatedField(many=True, read_only=True,
                                                    help_text='URL list of Withdrawals bys user',
                                                    view_name='cashcall-detail')

    class Meta:
        model = User
        fields = ['url', 'id', 'email', 'full_name', 'phone_number',
                  'user_balance', 'date_joined', 'refill', 'cash_call']
        read_only_fields = ['email', 'full_name', 'is_active', 'user_balance']

    def get_user_balance(self, obj):
        user = obj
        return user.user_balance.get().balance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(min_length=8, max_length=100, required=True,
                                         write_only=True,
                                         help_text='User Password, must be at least 8characters',
                                         style={'input_type': 'password'})
    new_password = serializers.CharField(min_length=8, max_length=100, required=True,
                                         write_only=True,
                                         help_text='User Password, must be at least 8characters',
                                         style={'input_type': 'password'})

    def validate_new_password(self, value):
        validate_password(value)
        return value


class UserAddressSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for the User Address model.
    """
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserAddress
        fields = ['user', 'url', 'street_address', 'city', 'state', 'country']
