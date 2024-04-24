from django.contrib import admin
from .models import Admin, Driver, Message, Request

# Register your models here.

admin.site.register([Admin, Driver, Message, Request])
