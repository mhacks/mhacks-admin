from django.db import models
from rest_framework.fields import CharField

from utils import GenericListCreateModel, GenericUpdateDestroyModel, NonNullPrimaryKeyField
from floors import FloorModel
from models import Any, MHacksModelSerializer


class LocationModel(Any):
    name = models.CharField(max_length=60)
    floor = models.ForeignKey(
        FloorModel, on_delete=models.PROTECT, null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)

    def __unicode__(self):
        if self.floor:
            return "{} on the {}".format(self.name, str(self.floor.name))
        return self.name


class LocationSerializer(MHacksModelSerializer):
    id = CharField(read_only=True)
    floor = NonNullPrimaryKeyField(many=False, pk_field=CharField(),
                                   queryset=FloorModel.objects.all().filter(deleted=False),
                                   allow_empty=True)

    class Meta:
        model = LocationModel
        fields = ('id', 'name', 'floor', 'latitude', 'longitude')


class LocationAPIView(GenericUpdateDestroyModel):
    serializer_class = LocationSerializer
    queryset = LocationModel.objects.all()


class LocationListAPIView(GenericListCreateModel):
    """
    Locations are specific important locations that can be linked to from other tables.
    """
    serializer_class = LocationSerializer
    query_set = LocationModel.objects.none()

    def get_queryset(self):
        date_last_updated = super(LocationListAPIView, self).get_queryset()
        if date_last_updated:
            return LocationModel.objects.all().filter(last_updated__gte=date_last_updated)
        else:
            return LocationModel.objects.all().filter(deleted=False)
