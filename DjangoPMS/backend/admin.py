from django.contrib import admin
from .models import Admin, Driver, Message, Request, ParkingLot, Slot
from leaflet.admin import LeafletGeoAdmin

# Register your models here.

admin.site.register([Admin, Driver, Message, Request, Slot])
# If model implements Geospatial data
admin.site.register(ParkingLot, LeafletGeoAdmin)
