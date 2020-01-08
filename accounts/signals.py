import smtplib
from .models import User, UserBalance
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserBalance.objects.create(user=instance)
        try:
            send_mail('Welcome to Muve',
                      f'thanks for signing up, {instance.full_name}!',
                      settings.EMAIL_HOST_USER, [instance.email])
        except smtplib.SMTPAuthenticationError:
            pass
