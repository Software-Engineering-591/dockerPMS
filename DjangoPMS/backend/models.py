from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class BaseUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Admin(BaseUser):
    pass


# Remember to run "python manage.py makemigrations" to create the model on the database
