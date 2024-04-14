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
    pass

class Payment(models.Model):
    PAYMENT_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('cash', 'Cash'),
        ('online', 'Online')
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    )
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    pay_time = models.DateTimeField(auto_now_add=True)
    # Link to the driver and the parking slot
    Driver = models.ForeignKey('Driver', on_delete=models.CASCADE)
    slot = models.ForeignKey('Slot', on_delete=models.CASCADE)

class Slot(models.Model):
    number = models.CharField(max_length=10)
    location = models.TextField()
    size = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
    price_per_hour = models.DecimalField(max_digits=5, decimal_places=2)
    # Links driver class
    current_driver = models.ForeignKey('Driver', on_delete=models.SET_NULL, null=True, blank=True)
