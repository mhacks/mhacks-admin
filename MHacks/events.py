from django.db import models
from rest_framework.fields import CharField, ChoiceField
from rest_framework.relations import PrimaryKeyRelatedField

from utils import GenericListCreateModel, GenericUpdateDestroyModel, UnixEpochDateField, DurationInSecondsField
from locations import LocationModel
from models import Any, MHacksModelSerializer


class EventModel(Any):
    name = models.CharField(max_length=60)
    info = models.TextField(default='')
    locations = models.ManyToManyField(LocationModel)
    start = models.DateTimeField()
    duration = models.DurationField()
    CATEGORIES = ((0, 'General'), (1, 'Logistics'),
                  (2, 'Food'), (3, 'Learn'), (4, 'Social'))
    category = models.IntegerField(choices=CATEGORIES)
    approved = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class EventSerializer(MHacksModelSerializer):
    id = CharField(read_only=True)
    start = UnixEpochDateField()
    locations = PrimaryKeyRelatedField(many=True, pk_field=CharField(),
                                       queryset=LocationModel.objects.all().filter(deleted=False))
    duration = DurationInSecondsField()
    category = ChoiceField(choices=EventModel.CATEGORIES)

    class Meta:
        model = EventModel
        fields = ('id', 'name', 'info', 'start', 'duration',
                  'locations', 'category', 'approved')


class EventAPIView(GenericUpdateDestroyModel):
    serializer_class = EventSerializer
    queryset = EventModel.objects.all()


class EventListAPIView(GenericListCreateModel):
    """
    Events are the objects that show up on the calendar view and represent
    specific planned events at the hackathon.
    """
    serializer_class = EventSerializer
    query_set = EventModel.objects.none()

    def get_queryset(self):
        date_last_updated = super(EventListAPIView, self).get_queryset()
        if date_last_updated:
            query_set = EventModel.objects.all().filter(last_updated__gte=date_last_updated)
        else:
            query_set = EventModel.objects.all().filter(deleted=False)
        if not self.request.user or not self.request.user.has_perm('MHacks.change_event'):
            return query_set.filter(approved=True)
        return query_set
