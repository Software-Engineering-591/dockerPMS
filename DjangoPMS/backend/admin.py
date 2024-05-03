from django.contrib import admin
from .models import Admin, Driver, Message, Request, ParkingLot
from leaflet.admin import LeafletGeoAdmin

# Register your models here.

admin.site.register([Admin, Driver, Message, Request])
# If model implements Geospatial data
admin.site.register(ParkingLot, LeafletGeoAdmin)
