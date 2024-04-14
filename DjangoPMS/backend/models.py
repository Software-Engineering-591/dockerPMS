from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.views import defaults


# Create your models here.


class BaseUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Admin(BaseUser):
    pass


class Driver(BaseUser):
    pass

class Slot(models.Model):
    pass

class Message(models.Model):
    Message_text = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(default=timezone.now)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender", default=User)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver", default=User)
    def __str__(self):
        return self.Message_text



class Request(models.Model):
    driver_id = models.ForeignKey(Driver, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    arrival = models.DateTimeField()
    departure = models.DateTimeField()
    class current_status(models.TextChoices):
        PENDING = "Pending"
        APPROVED = "Approved"
        REJECTED = "Rejected"

    status = models.CharField(
        max_length=8,
        choices=current_status.choices,
        default=current_status.PENDING,
    )




