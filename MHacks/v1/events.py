from MHacks.models import Event as EventModel
from MHacks.v1.serializers import EventSerializer
from MHacks.v1.util import GenericListCreateModel, GenericUpdateDestroyModel


class Events(GenericListCreateModel):
    """
    Events are the objects that show up on the calendar view and represent specific planned events at the hackathon.
    """
    serializer_class = EventSerializer
    query_set = EventModel.objects.none()

    def get_queryset(self):
        date_last_updated = super(Events, self).get_queryset()
        if date_last_updated:
            query_set = EventModel.objects.all().filter(last_updated__gte=date_last_updated)
        else:
            query_set = EventModel.objects.all().filter(deleted=False)
        if not self.request.user or not self.request.user.has_perm('MHacks.change_event'):
            return query_set.filter(approved=True)
        return query_set


class Event(GenericUpdateDestroyModel):
    serializer_class = EventSerializer
    queryset = EventModel.objects.all()
