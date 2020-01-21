from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.functional import cached_property
from django.core.validators import RegexValidator
# Create your accounts models here.


class UserManager(BaseUserManager):
    """Defines a model manager for User model."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User model."""
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(_('full name'), max_length=64, blank=True)
    phone_regex = RegexValidator(regex=r'^s*[0][7-9]\d{9,11}$',
                                 message="Phone number must be entered in the format: '08012345678'. "
                                         "11 digits allowed.")
    phone_number = models.CharField(_('phone number'), validators=[phone_regex],
                                    unique=True, max_length=11, blank=True, null=True)
    paystack_costumer_id = models.IntegerField(_('Paystack costumer Id'), unique=True, blank=True, null=True)
    paystack_authorization_code = models.CharField(max_length=16, blank=True, null=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_staff = models.BooleanField(_('is staff'), default=False)
    is_superuser = models.BooleanField(_('is superuser'), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['date_joined']

    def __str__(self):
        return self.full_name

    @cached_property
    def balance(self):
        if hasattr(self, 'user_balance'):
            return self.user_balance.get().balance
        return None


class UserBalance(models.Model):
    """A model for the users balance"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_balance')
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)

    def __str__(self):
        return str(self.balance)

    def __unicode__(self):
        return str(self.balance)


class UserAddress(models.Model):
    """ An address model with a many to one relationship with the user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address')
    street_address = models.CharField(max_length=128)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    country = models.CharField(max_length=64)

    def __str__(self):
        return self.street_address

    # def get_absolute_url(self):
    #     return reverse('home', kwargs={})

    class Meta:
        """for django admin"""
        verbose_name = _('user address')
        verbose_name_plural = _('user addresses')
        ordering = ['user']
