from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class BaseUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Admin(BaseUser):
    pass


class Driver(BaseUser):
    credit = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


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
