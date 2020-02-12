import smtplib
from .models import Refill, CashCall
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
import logging.config
import logging
from pypaystack import Transaction
import time
import threading
import decimal

# Get an instance of a logger
logger = logging.getLogger(__name__)

logging.config.dictConfig(settings.LOGGING)


@receiver(post_save, sender=CashCall)
@receiver(post_save, sender=Refill)
def balance_update(sender, instance, created, **kwargs):
    """
    A function to sends alerts whenever a transaction is completed
    :param sender: Model that handles the transaction
    :param instance: An instance of the sender model.
            contains transaction details
    :param created: Bool. If a new instance of the model was created
    :param kwargs: keyword arguments
    :return: None
    """
    email_subject = "Muve Alert"
    if sender == Refill:
        alert_type = "credited"
    elif sender == CashCall:
        alert_type = "debited"
    else:
        alert_type = None
    if (sender == Refill and instance.verified) or (sender == CashCall):
        try:
            if alert_type is not None:
                message = f'Dear {instance.user.full_name},\n ' \
                          f'your Muve Money wallet has been {alert_type} with the sum of N{instance.amount}\n' \
                          f'on {instance.date_deposited.strftime("%Y-%m-%d %H:%M")}\n' \
                          f'your current balance is N{instance.current_balance}'
            else:
                message = ""
            send_mail(subject=email_subject, message=message,
                      from_email=settings.EMAIL_HOST_USER,
                      recipient_list=[instance.user.email])
            logger.info("message sent")
        except smtplib.SMTPAuthenticationError as se:
            logger.error("email send error", se)
        except Exception as e:
            logger.error("email send error", e)


@receiver(post_save, sender=Refill)
def deposit_verify(sender, instance, created, **kwargs):
    if instance.reference and created and not instance.verified:
        t = threading.Thread(target=deposit_verify_thread, args=[instance])
        t.setDaemon(True)
        t.start()


def deposit_verify_thread(instance, test=False):
    paystack_transaction = Transaction(authorization_key=settings.PAYSTACK_PUBLIC_KEY)
    status = False
    count = 0
    while not status and count < 5:
        if not test:
            time.sleep(60)
        response = paystack_transaction.verify(instance.reference)
        print(response)
        if response[3]['status'] == 'success':
            instance.verified = True
            with transaction.atomic():
                balance = instance.user.user_balance.get()
                balance.balance = decimal.Decimal(response[3]['amount'] / 100) + balance.balance
                balance.save(force_update=True)
            if not instance.user.paystack_authorization_code:
                if response[3]['authorization']['reusable']:
                    instance.user.paystack_authorization_code = \
                        response[3]['authorization']['authorization_code']
                    print('paystack auth code added')
            instance.save()
            instance.user.save()
            return None
        count += 1
    return None



