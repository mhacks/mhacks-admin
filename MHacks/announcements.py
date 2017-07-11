from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from rest_framework.fields import CharField

from utils import GenericListCreateModel, GenericUpdateDestroyModel, UnixEpochDateField
from models import Any, MHacksModelSerializer


class AnnouncementModel(Any):
    title = models.CharField(max_length=60)
    info = models.TextField(default='')
    broadcast_at = models.DateTimeField()
    category = models.PositiveIntegerField(validators=[MinValueValidator(0),
                                                       MaxValueValidator(31)], help_text="0 for none; 1 for emergency; 2 for logistics; 4 for food; 8 for event; Add 16 to make sponsored")
    approved = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)

    @staticmethod
    def max_category():
        return 31

    def __unicode__(self):
        return self.title


class AnnouncementSerializer(MHacksModelSerializer):
    id = CharField(read_only=True)
    broadcast_at = UnixEpochDateField()

    class Meta:
        model = AnnouncementModel
        fields = ('id', 'title', 'info', 'broadcast_at', 'category', 'approved')


class AnnouncementAPIView(GenericUpdateDestroyModel):
    serializer_class = AnnouncementSerializer
    queryset = AnnouncementModel.objects.all()


class AnnouncementListAPIView(GenericListCreateModel):
    """
    Announcements are what send push notifications and are useful for pushing updates to MHacks participants.
    Anybody who is logged in can make a GET request where as only authorized users can create, update and delete them.
    """
    serializer_class = AnnouncementSerializer
    query_set = AnnouncementModel.objects.none()

    def get_queryset(self):
        date_last_updated = super(AnnouncementListAPIView, self).get_queryset()

        if not self.request.user or not self.request.user.has_perm('MHacks.change_announcement'):
            query_set = AnnouncementModel.objects.all().filter(approved=True).filter(broadcast_at__lte=timezone.now())
            if date_last_updated:
                query_set = query_set.filter(Q(last_updated__gte=date_last_updated) | Q(broadcast_at__gte=date_last_updated))
            else:
                query_set = query_set.filter(deleted=False)
        else:
            query_set = AnnouncementModel.objects.all()
            if date_last_updated:
                query_set = query_set.filter(last_updated__gte=date_last_updated)
            else:
                query_set = query_set.filter(deleted=False)
        return query_set



