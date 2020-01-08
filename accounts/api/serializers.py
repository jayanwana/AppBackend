from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.hashers import make_password
from accounts.models import User, UserBalance, UserAddress


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    User Registration Form. Creates new instances of the User model
    """
    email = serializers.EmailField(required=True,
                                   help_text='User Email Address. Required in email format',
                                   validators=[UniqueValidator(queryset=User.objects.all(),
                                                               message=
                                                               "An account with this email already exists")])
    full_name = serializers.CharField(max_length=64, required=True,
                                      help_text='Full name of the User',)
    password = serializers.CharField(min_length=8, max_length=100, required=True,
                                     write_only=True, help_text='User Password, must be at least 8characters',
                                     style={'input_type': 'password'})
    confirm_password = serializers.CharField(min_length=8, max_length=100, required=True,
                                             help_text='Re-enter password for confirmation',
                                             write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ("id", "full_name", "email",
                  "password", "confirm_password", "date_joined")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].error_messages['required'] = 'Email is required'
        self.fields['email'].error_messages['blank'] = 'Email cannot be blank'
        self.fields['email'].error_messages['unique'] = 'User with email already exists'
        self.fields['full_name'].error_messages['required'] = 'Full name is required'
        self.fields['full_name'].error_messages['blank'] = 'Full name cannot be blank'
        self.fields['password'].error_messages['required'] = 'Password is required'
        self.fields["password"].error_messages["min_length"] = "password must be at least 8 characters"

    def create(self, validated_data):
        """
        Create an instance of the user model
        :param validated_data:
        :return:
        """
        user = User.objects.create(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=make_password(validated_data['password']))
        return user

    def validate(self, attrs):
        """ Make sure Passwords match"""
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Those passwords don't match.")
        return attrs


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
        fields = ['url', 'id', 'email', 'full_name',
                  'user_balance', 'date_joined', 'refill', 'cash_call']
        read_only_fields = ['email', 'full_name', 'is_active', 'user_balance']

    def get_user_balance(self, obj):
        user = obj
        return user.user_balance.get().balance


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
