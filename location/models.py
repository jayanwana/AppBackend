# from django.db import models
from django.contrib.gis.db import models
from accounts.models import User

# Create your models here.


class Agent(models.Model):
    user = models.ForeignKey(User, models.CASCADE, 'agent')
    location = models.PointField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.user.full_name

