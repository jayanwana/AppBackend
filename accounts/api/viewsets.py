from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from .serializers import UserSerializer, UserRegistrationSerializer, UserAddressSerializer
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
        Return the a particular User.

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


class UserRegistrationAPIView(viewsets.generics.CreateAPIView):
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
