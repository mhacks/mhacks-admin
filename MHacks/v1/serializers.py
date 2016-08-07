from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView

# Extends auth token serializer to accommodate push notifs
class AuthSerializer(AuthTokenSerializer):
    token = serializers.CharField()
    is_gcm = serializers.BooleanField()

    def validate(self, attrs):
        # check if the token exist
        token = attrs.get('token')
        is_gcm = attrs.get('is_gcm')

        if 'token' not in attrs.keys():
            msg = ('token not specified')
            raise serializers.ValidationError(msg)

        if 'is_gcm' not in attrs.keys():
            msg = ('is_gcm not specified')
            raise serializers.ValidationError(msg)

        attrs = super(AuthSerializer, self).validate(attrs)

        attrs['push_notification'] = {
            'token': token,
            'is_gcm': is_gcm
        }

        return attrs


class UnixEpochDateField(serializers.DateTimeField):
    def to_internal_value(self, value):
        from datetime import datetime

        try:
            val = float(value)
            if val < 0:
                raise ValueError
            date = datetime.fromtimestamp(val)
            from pytz import utc

            date = date.replace(tzinfo=utc)
            return date
        except ValueError:
            self.fail('invalid', format='Unix Epoch Timestamp')

    def to_representation(self, value):
        import datetime

        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            self.fail('date')
        dt = to_utc_epoch(value)
        if not dt:
            self.fail('invalid', format='Unix Epoch Timestamp')
        return dt


class DurationInSecondsField(serializers.Field):
    error_messages = {'invalid': 'Invalid format expected duration in seconds'}

    def to_internal_value(self, data):
        from datetime import timedelta

        try:
            return timedelta(seconds=int(data))
        except ValueError:
            self.fail('invalid')

    def to_representation(self, value):
        return value.total_seconds()


class GenericListCreateModel(CreateAPIView, ListAPIView):
    permission_classes = (DjangoModelPermissions,)

    def __init__(self):
        self.date_of_update = None
        super(GenericListCreateModel, self).__init__()

    def get_queryset(self):
        self.date_of_update = now_as_utc_epoch()
        return parse_date_last_updated(self.request)

    def list(self, request, *args, **kwargs):
        response = super(GenericListCreateModel, self).list(request, *args, **kwargs)
        response.data = {'results': response.data, 'date_updated': self.date_of_update}
        return response

    def create(self, request, *args, **kwargs):
        if hasattr(self, 'get_queryset'):
            queryset = self.get_queryset()
        else:
            queryset = getattr(self, 'queryset', None)

        assert queryset is not None, (
            'Cannot have a GenericListModel with no '
            '`.queryset` or not have defined the `.get_queryset()` method.'
        )
        model_class = queryset.model

        request.data['approved'] = request.user.has_perm('%(app_label)s.change_%(model_name)s' %
                                                         {'app_label': model_class._meta.app_label,
                                                          'model_name': model_class._meta.model_name})

        return super(GenericListCreateModel, self).create(request, *args, **kwargs)


class GenericUpdateDestroyModel(RetrieveUpdateDestroyAPIView):
    permission_classes = (DjangoModelPermissions,)
    lookup_field = 'id'


class MHacksModelSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        if getattr(instance, 'deleted', False):
            return {instance._meta.pk.name: str(instance.pk), 'deleted': True}
        return super(MHacksModelSerializer, self).to_representation(instance)


def parse_date_last_updated(request):
    date_last_updated_raw = request.query_params.get('since', None)
    if date_last_updated_raw:
        try:
            from pytz import utc
            from datetime import datetime

            return datetime.utcfromtimestamp(float(date_last_updated_raw)).replace(tzinfo=utc)
        except ValueError:
            pass
    return None


def now_as_utc_epoch():
    from django.utils.timezone import now

    return to_utc_epoch(now())


def to_utc_epoch(date_time):
    from datetime import datetime

    if isinstance(date_time, datetime):
        from calendar import timegm

        return timegm(date_time.timetuple())
    return None
