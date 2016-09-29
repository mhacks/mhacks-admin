from MHacks.models import Floor as FloorModel
from MHacks.v1.serializers import FloorSerializer
from MHacks.v1.util import GenericListCreateModel, GenericUpdateDestroyModel


class Floors(GenericListCreateModel):
    """
    Floors are the new map object
    """
    serializer_class = FloorSerializer
    query_set = FloorModel.objects.none()

    def get_queryset(self):
        date_last_updated = super(Floors, self).get_queryset()
        if date_last_updated:
            query_set = FloorModel.objects.all().filter(last_updated__gte=date_last_updated)
        else:
            query_set = FloorModel.objects.all().filter(deleted=False)
        return query_set


class Floor(GenericUpdateDestroyModel):
    serializer_class = FloorSerializer
    queryset = FloorModel.objects.all().filter(deleted=False)
