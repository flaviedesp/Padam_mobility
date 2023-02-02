from django.contrib import admin

from .filters import DriverFilter
from .forms import BusStopAdminForm, BusStopInBusShiftForm, BusShiftAdminForm
from .models import (BusShift, BusStop, BusStopInBusShift, )


@admin.register(BusStop)
class BusStopAdmin(admin.ModelAdmin):
    # form = BusStopAdminForm
    list_display = ("name_place", "stop",)

    list_filter = ("place__name",)

    search_fields = ("name_place", "stop",)


    def name_place(self, obj):
        return obj.place.name

    name_place.short_description = "Nom de l'arret"


class BusShiftBusStopInLine(admin.TabularInline):
    model = BusStopInBusShift
    # fields = ("bus_shift", "bus_stop", "order", "date",)
    form = BusStopInBusShiftForm
    extra = 2
    min_num = 2


@admin.register(BusShift)
class BusShiftAdmin(admin.ModelAdmin):
    form = BusShiftAdminForm
    list_display = ("name_bus", "name_driver", "heure_depart", "heure_arrive", "time_total",)
    list_filter = ("bus__licence_plate", DriverFilter,)
    search_fields = ("bus__licence_plate", "driver__last_name", "driver__first_name")
    exclude = ("stop",)
    raw_id_fields=("driver", "bus")

    def name_bus(self, obj):
        return obj.bus.licence_plate

    name_bus.short_description = "Nom du bus"

    def name_driver(self, obj):
        return f"{obj.driver.first_name} {obj.driver.last_name}"

    name_driver.short_description = "Nom du Chauffeur"

    inlines = (BusShiftBusStopInLine,)
