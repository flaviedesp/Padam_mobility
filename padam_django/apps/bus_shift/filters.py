from django.contrib import admin


from ..users.models import User


class DriverFilter(admin.SimpleListFilter):
    title = "Nom du chauffeur"

    parameter_name = "driver_ full_name"

    def lookups(self, request, model_admin):
        return [
            (driver.id, driver.last_name + " " + driver.first_name)
            for driver in User.objects.all()
            .order_by("last_name", "first_name")
            .only("id", "last_name", "first_name")
            .distinct()
        ]

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(driver__id=self.value())
        return queryset
