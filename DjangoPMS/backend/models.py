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



class Message(models.Model):
        Message_text = models.TextField(max_length=1000)
        timestamp = models.DateTimeField(default=timezone.now)
        sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender", null=False)
        receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver", null=False)
        def __str__(self):
            return self.Message_text



class Request(models.Model):
    driver_id = models.ForeignKey(Driver, on_delete=models.CASCADE, null=False)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, null=False)
    arrival = models.DateTimeField()
    departure = models.DateTimeField()
    class current_status(models.TextChoices):
        PENDING = "Pending"
        APPROVED = "Approved"
        REJECTED = "Rejected"

    status = models.CharField(max_length=8, choices=current_status.choices, default=current_status.PENDING)


class Payment(models.Model):
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    timestamp = models.DateTimeField(auto_now=True)
    # Link to the driver and the parking slot
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)


class Slot(models.Model):
    class Status(models.TextChoices):
        RESERVED = "R"
        AVAILABLE = "A"
        DISABLED = "D"

    status = models.CharField(choices=Status, max_length=1, default=Status.AVAILABLE)
    number = models.CharField(max_length=10)

    # Links driver class
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, default=None)

