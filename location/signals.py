from .models import Agent
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User


@receiver(post_save, sender=Agent)
def activate_agent_status(sender, instance, created, **kwargs):
    if created:
        agent = User.objects.get(pk=instance.user.id)
        agent.is_agent = True
        agent.save()
