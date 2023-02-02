from django.db import models


class BusStop(models.Model):
    """
    correspond a un arret
    Cette classe est, je pense, non utile, a voir
    on pourrait faire la liaison directement avec geographie mais si on souhaite a jouer des varaibles specifiques,
    il faudra le faire là
    """
    place = models.OneToOneField("geography.Place", on_delete=models.CASCADE,
                                 null=False)  # un arret pour un point geographique
    stop = models.DateTimeField(blank=True, default="", null=True)

    def __str__(self):
        return f"Stop: {self.place.name} - {self.stop.hour}" if self.stop else f"Stop: {self.place.name}"

    class Meta:
        verbose_name = ("BusStop")
        verbose_name_plural = ("BusStops")


class BusShift(models.Model):
    """correspond a un trajet"""
    bus = models.OneToOneField("fleet.Bus", on_delete=models.CASCADE, null=True, blank=True)  # un bus par trajet
    driver = models.OneToOneField("users.User", on_delete=models.CASCADE, null=False)  # un chauffeur par bus par trajet
    stop = models.ManyToManyField("bus_shift.BusStopInBusShift", verbose_name="stop")


    @property
    def time_total(self):
        """renvoie un datetime contenant la difference sous le format timedelta"""

        return (self.heure_arrive - self.heure_depart) if self.heure_arrive and self.heure_depart  else "-"

    @property
    def heure_depart(self):
        """
        correspond au premier arret
        on part du principe que le BusStop existe aussi non, il faudrait gérer l'erreur
        """
        bus_stop_first = BusStopInBusShift.objects.filter(bus_shift=self.pk).order_by("order").first()
        return bus_stop_first.date if bus_stop_first else None

    @property
    def heure_arrive(self):
        """
        correspond au dernier arret
        on part du principe que le BusStop existe
        """
        bus_stop_last = BusStopInBusShift.objects.filter(bus_shift=self.pk).order_by("order").last()
        return bus_stop_last.date if bus_stop_last else None

    class Meta:
        verbose_name = ("BusShift")
        verbose_name_plural = (u"BusShifts")


class BusStopInBusShift(models.Model):
    bus_shift = models.ForeignKey(BusShift, verbose_name="Bus Stop", on_delete=models.PROTECT, blank=True, null=True)
    bus_stop = models.ForeignKey(BusStop, verbose_name="Bus Stop", blank=True, null=True, on_delete=models.PROTECT)
    order = models.PositiveSmallIntegerField(blank=True, null=False, default="")
    date = models.DateTimeField(null=True, blank=True, default="")

    class Meta:
        verbose_name= "Bus Stop In Bus Shift"
        verbose_name_plural= "Bus Stops In Bus Shifts"

1
