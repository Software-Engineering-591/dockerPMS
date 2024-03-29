from django.contrib import admin
from .models import Admin, Driver

# Register your models here.

admin.site.register([Admin, Driver])
