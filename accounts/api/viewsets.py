from rest_framework import viewsets, status, generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from .serializers import (UserSerializer, UserRegistrationSerializer,
                          UserAddressSerializer, ChangePasswordSerializer)
from accounts.models import User, UserAddress


class IsUserOrAdmin(BasePermission):
    """
    Custom permission to give users access to their detailview.
    Admin users however have access to all.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj == request.user


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    retrieve:
        Return the User matching the Id.

    list:
        Return a list of all Users if Admin User.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrAdmin,)

    def get_queryset(self):
        """
        Filter objects so a user only sees his own stuff.
        If user is admin, let him see all.
        """
        if self.request.user.is_staff:
            return self.queryset
        else:
            return self.queryset.filter(id=self.request.user.id)


class UpdatePassword(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            old_password = serializer.validated_data.get("old_password")
            if not self.object.check_password(str(old_password)):
                return Response({"old_password": ["Wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationAPIView(generics.CreateAPIView):
    """
    User Registration Form API View. Creates new instances of the User model
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        """
        New User registration Form
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = serializer.instance
        token = Token.objects.create(user=user)
        data = serializer.data
        data["token"] = token.key
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class UserAddressViewSet(viewsets.ModelViewSet):
    """
    retrieve:
        Return a particular address of a User.

    list:
        Return a list of all addresses of a user.

    create:
        Add a new Address.

    destroy:
        Delete an Address.

    update:
        Update an Address.

    partial_update:
        Update an Address.
    """
    queryset = UserAddress.objects.all()
    serializer_class = UserAddressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user)
        return query_set
