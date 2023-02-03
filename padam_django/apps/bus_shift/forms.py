from django import forms
from django.core.exceptions import ValidationError

from .models import BusShift, BusStop, BusStopInBusShift


class BusStopAdminForm(forms.ModelForm):
    class Meta:
        model = BusStop
        exclude = ("stop",)
        field = (
            "bus",
            "driver",
        )


class BusShiftAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class BusStopInBusShiftForm(forms.ModelForm):
    def clean(self):
        errors = {}
        cleaned_data = super().clean()
        if cleaned_data:
            errors.update(validate_block_bus_stop(cleaned_data))
        if errors:
            raise ValidationError(errors)
        return cleaned_data

    class Meta:
        model = BusStopInBusShift
        fields = "__all__"


def validate_block_bus_stop(cleaned_data) -> dict:
    """
    Permet de verifier plusieurs point important:
     - un bus ne peux pas avoir plusieurs trajet en meme temps
     - un driver ne peux pas avoir plusieurs trajet en meme temps
     - la date du premier stop doit etre inferieur a la date du stop suivant
     - il y a au minimum 2 stops
     - un order differents de 0 et unique est obligatoire
    """

    errors = {}
    # on verifie si il y a deja des enregistrement pour ce trajets
    from .models import BusStopInBusShift

    if cleaned_data.get("order"):
        stops = BusStopInBusShift.objects.filter(
            bus_shift=cleaned_data.get("bus_shift")
        ).order_by("order")
        if stops:
            order = stops.values_list("order", flat=True)
            if cleaned_data.get("order") == 0:
                errors[
                    "order"
                ] = "il est obligatoire de remplir l'order de passage des arrets (ne pas mettre 0)"
            elif cleaned_data.get("order") in order:
                if cleaned_data.get(
                    "bus_stop"
                ).pk != BusStopInBusShift.objects.values_list(
                    "bus_stop__id", flat=True
                ).get(
                    bus_stop__id=(cleaned_data.get("bus_stop").pk)
                ):
                    errors["order"] = "il est obligatoire de remplir des orders uniques"
        else:
            pass
    if cleaned_data["date"]:
        stops = BusStopInBusShift.objects.filter(
            bus_shift=cleaned_data.get("bus_shift")
        ).order_by("date")
        if stops:
            if cleaned_data["order"] != 1:
                if stops.filter(order=cleaned_data["order"] - 1).exists():
                    if (
                        cleaned_data["date"]
                        < stops.get(order=cleaned_data["order"] - 1).date
                    ):
                        errors["date"] = "Il y a une erreur de date"
        else:
            pass
        bus_driver = cleaned_data.get("bus_shift")
        # on verifie que le bus est dispo
        bus_non_dispos = BusShift.objects.filter(bus__id=bus_driver.bus.id)
        if bus_non_dispos:
            for bus in bus_non_dispos:

                if bus.heure_depart <= cleaned_data["date"] <= bus.heure_arrive and (
                    bus_driver.pk != bus.pk
                ):
                    errors["date"] = "Le bus est déja pris dans ces horaires"
                    break
        # on verifie que le chauffeur est dispo
        driver_non_dispos = BusShift.objects.filter(driver__id=bus_driver.driver.id)
        if driver_non_dispos:
            for driver in driver_non_dispos:
                if driver.heure_depart <= cleaned_data[
                    "date"
                ] <= driver.heure_arrive and (bus_driver.pk != driver.pk):
                    errors["date"] = "Le chauffeur est déja occupé dans ces horaires"
                    break

    return errors
