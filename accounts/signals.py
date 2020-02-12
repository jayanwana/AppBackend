import smtplib
from .models import User, UserBalance
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created, post_password_reset
from django.urls import reverse
from pypaystack import Customer


@receiver(post_save, sender=User)
def initiate_paystack_customer(sender, instance, created, **kwargs):
    """
    Create an instance of the paystack customer class whenever a new user is created
    :param sender: User model
    :param instance: an instance of the user model that is being saved
    :param created: bool. If a new user is being created
    :param kwargs: extra keyword arguments
    :return: None
    """
    full_name = str(instance.full_name)
    if created and not full_name.startswith('Test'):
        full_name = full_name.split()
        customer = Customer(settings.PAYSTACK_PUBLIC_KEY)
        try:
            response = customer.create(instance.email, full_name[0],
                                       full_name[1], instance.phone_number)  # Add new customer
            instance.paystack_costumer_id = response[3]['id']
            instance.save()
        except Exception as e:
            print(e)
        except ConnectionError as e:
            print(e)


@receiver(post_save, sender=User)
def create_user_balance(sender, instance, created, **kwargs):
    """
    Create a new user balance object whenever a new user is created
    :param sender: User model
    :param instance: an instance of the user model that is being saved
    :param created: bool. If a new user is being created
    :param kwargs: extra keyword arguments
    :return: None
    """
    if created:
        # If a new user, create a user balance for user.
        UserBalance.objects.create(user=instance)
        try:
            send_mail('Welcome to Muve',
                      f'thanks for signing up, {instance.full_name}!',
                      settings.EMAIL_HOST_USER, [instance.email])
        except smtplib.SMTPAuthenticationError:
            pass


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: Password reset View
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'full_name': reset_password_token.user.full_name,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(reverse('password_reset:reset-password-request'),
                                                   reset_password_token.key)
    }

    # render email text
    # email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Muve"),
        # message:
        email_plaintext_message,
        # from:
        "muveapi@gmail.com",
        # to:
        [reset_password_token.user.email]
    )
    # msg.attach_alternative(email_html_message, "text/html")
    msg.send()


@receiver(post_password_reset)
def password_reset_confirm(user, *args, **kwargs):
    try:
        send_mail('Muve Password reset',
                  f'Dear {user.full_name}, your password reset was successful',
                  settings.EMAIL_HOST_USER, [user.email])
    except smtplib.SMTPAuthenticationError:
        pass
