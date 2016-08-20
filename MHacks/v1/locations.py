from MHacks.models import Location as LocationModel
from MHacks.v1.serializers import LocationSerializer
from MHacks.v1.util import GenericListCreateModel, GenericUpdateDestroyModel


class Locations(GenericListCreateModel):
    """
    Locations are specific important locations that can be linked to from other tables.
    """
    serializer_class = LocationSerializer
    query_set = LocationModel.objects.none()

    def get_queryset(self):
        date_last_updated = super(Locations, self).get_queryset()
        if date_last_updated:
            return LocationModel.objects.all().filter(last_updated__gte=date_last_updated)
        else:
            return LocationModel.objects.all().filter(deleted=False)


class Location(GenericUpdateDestroyModel):
    serializer_class = LocationSerializer
    queryset = LocationModel.objects.all()
