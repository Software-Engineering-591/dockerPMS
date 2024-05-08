from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.gis.db import models as gis_models
from django.db.models import Q

# Create your models here.


class BaseUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True
    @property
    def messages(self):
        return Message.objects.filter(Q(sender=self.user) | Q(receiver=self.user))
    def send_message(self, message):
        Message.objects.create(sender=self.user, message_text=message.message_text, receiver=message.receiver)


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

class Message(models.Model):
    message_text = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(default=timezone.now)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sender'
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='receiver'
    )

    def __str__(self):
        return self.message_text

class ParkingLot(models.Model):
    poly = gis_models.PolygonField(geography=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)

    def get_total_space(self):
        return Slot.objects.all().filter(lot=self.id).count()

    def get_reserved_space(self):
        return Slot.objects.filter(status='R', lot=self.id).count()

    def get_available_space(self):
        return Slot.objects.filter(status='A', lot=self.id).count()

class Slot(models.Model):
    class Status(models.TextChoices):
        RESERVED = 'R'
        AVAILABLE = 'A'
        DISABLED = 'D'

    status = models.CharField(
        choices=Status, max_length=1, default=Status.AVAILABLE
    )
    number = models.CharField(max_length=10)

    # Links driver class
    driver = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, default=None, blank=True
    )
    lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, null=True, default=None)

class Request(models.Model):
    driver_id = models.ForeignKey(Driver, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    arrival = models.DateTimeField()
    departure = models.DateTimeField()
    timestamp = models.DateTimeField(default=timezone.now)

    class CurrentStatus(models.TextChoices):
        PENDING = 'P'
        APPROVED = 'A'
        REJECTED = 'R'

    status = models.CharField(
        max_length=1, choices=CurrentStatus, default=CurrentStatus.PENDING
    )

