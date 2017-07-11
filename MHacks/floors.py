from django.db import models
from rest_framework.fields import CharField

from utils import GenericListCreateModel, GenericUpdateDestroyModel
from models import Any, MHacksModelSerializer


class FloorModel(Any):
    name = models.CharField(max_length=60)
    index = models.IntegerField(unique=True)
    image = models.URLField()
    description = models.TextField(blank=True)
    offset_fraction = models.FloatField(default=1.0, null=True, blank=True)
    aspect_ratio = models.FloatField(default=1.0, null=True, blank=True)
    # Only used for maps ground overlay
    nw_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    nw_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    se_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    se_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __unicode__(self):
        return '{} displayed at index {}'.format(self.name, str(self.index))


class FloorSerializer(MHacksModelSerializer):
    id = CharField(read_only=True)

    class Meta:
        model = FloorModel
        fields = ('id', 'name', 'image', 'index', 'offset_fraction', 'aspect_ratio', 'description', 'nw_latitude',
                  'nw_longitude', 'se_latitude', 'se_longitude')


class FloorAPIView(GenericUpdateDestroyModel):
    serializer_class = FloorSerializer
    queryset = FloorModel.objects.all().filter(deleted=False)


class FloorListAPIView(GenericListCreateModel):
    """
    Floors are the new map object
    """
    serializer_class = FloorSerializer
    query_set = FloorModel.objects.none()

    def get_queryset(self):
        date_last_updated = super(FloorListAPIView, self).get_queryset()
        if date_last_updated:
            query_set = FloorModel.objects.all().filter(last_updated__gte=date_last_updated)
        else:
            query_set = FloorModel.objects.all().filter(deleted=False)
        return query_set
