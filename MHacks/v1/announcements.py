from django.utils import timezone

from MHacks.models import Announcement as AnnouncementModel
from MHacks.v1.serializers import AnnouncementSerializer
from MHacks.v1.util import GenericListCreateModel, GenericUpdateDestroyModel


class Announcements(GenericListCreateModel):
    """
    Announcements are what send push notifications and are useful for pushing updates to MHacks participants.
    Anybody who is logged in can make a GET request where as only authorized users can create, update and delete them.
    """
    serializer_class = AnnouncementSerializer
    query_set = AnnouncementModel.objects.none()

    def get_queryset(self):
        date_last_updated = super(Announcements, self).get_queryset()
        if date_last_updated:
            query_set = AnnouncementModel.objects.all().filter(last_updated__gte=date_last_updated)
        else:
            query_set = AnnouncementModel.objects.all().filter(deleted=False)
        if not self.request.user.has_perm('mhacks.change_announcement'):
            return query_set.filter(approved=True).filter(broadcast_at__lte=timezone.now())
        return query_set


class Announcement(GenericUpdateDestroyModel):
    serializer_class = AnnouncementSerializer
    queryset = AnnouncementModel.objects.all()
