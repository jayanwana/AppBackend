from django.db import models, transaction

# Create your models here.
# from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from accounts.models import UserAddress

User = settings.AUTH_USER_MODEL


class Refill(models.Model):
    """
    Model to handle Deposits, address is included to match cash call model
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refill')
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        validators=[
            MinValueValidator(float('50.00'))
        ]
    )
    date_deposited = models.DateTimeField(auto_now_add=True)
    current_balance = models.DecimalField(
        null=True,
        blank=True,
        decimal_places=2,
        max_digits=9,
        )
    previous_balance = models.DecimalField(
        null=True,
        blank=True,
        decimal_places=2,
        max_digits=9,
    )
    verified = models.BooleanField(default=False)
    reference = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f'{self.user} Refill {self.pk}'

    def get_absolute_url(self):
        return reverse('api:refill-detail')

    # def save(self, *args, **kwargs):
    #     """Save the transaction details and update the users balance"""
    #     with transaction.atomic():
    #         balance = self.user.user_balance.get()
    #         self.previous_balance = balance.balance
    #         balance.balance += self.amount
    #         self.current_balance = balance.balance
    #         super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date_deposited']


class CashCall(models.Model):
    """
    Model to handle Withdrawals
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cash_call')
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=9,
        validators=[
            MinValueValidator(float('50.00'))
        ]
    )
    date_deposited = models.DateTimeField(auto_now_add=True)
    current_balance = models.DecimalField(
        null=True,
        blank=True,
        decimal_places=2,
        max_digits=9,
        validators=[
            MinValueValidator(float('0.00'))
        ]
        )
    previous_balance = models.DecimalField(
        null=True,
        blank=True,
        decimal_places=2,
        max_digits=9,
        validators=[
            MinValueValidator(float('0.00'))
        ]
        )
    # verified = models.BooleanField(default=False)
    reference = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f'{self.user} Cash Call {self.pk}'

    def get_absolute_url(self):
        return reverse('api:cash_call-detail')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            balance = self.user.user_balance.get()
            self.previous_balance = balance.balance
            balance.balance -= self.amount
            balance.save()
            self.current_balance = balance.balance
            super().save(*args, **kwargs)

    def get_user_address(self):
        try:
            address = [(u.id, u.street_address) for u in self.user.address.all()]
        except AttributeError:
            address = list(tuple())
        return address

    class Meta:
        ordering = ['-date_deposited']


class Transaction(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='transaction')
    transaction_type = models.ForeignKey(ContentType, models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('transaction_type', 'object_id')
    reference_no = models.PositiveIntegerField(unique=True)
    amount = models.DecimalField(decimal_places=2,
                                 max_digits=9,
                                 validators=[MinValueValidator(float('50.00'))]
                                 )
    auth_code = models.CharField(max_length=64, blank=True, null=True)
    reusable_auth = models.BooleanField(blank=True, null=True)
