from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.fields import CharField, ChoiceField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from MHacks.models import Announcement as AnnouncementModel
from MHacks.models import Event as EventModel
from MHacks.models import Location as LocationModel
from MHacks.models import MHacksUser as MHacksUserModel
from MHacks.models import Ticket as TicketModel
from MHacks.v1.serializers.util import UnixEpochDateField, DurationInSecondsField


class MHacksModelSerializer(ModelSerializer):
    def to_representation(self, instance):
        if getattr(instance, 'deleted', False):
            return {instance._meta.pk.name: str(instance.pk), 'deleted': True}
        return super(MHacksModelSerializer, self).to_representation(instance)


class AnnouncementSerializer(MHacksModelSerializer):
    id = CharField(read_only=True)
    broadcast_at = UnixEpochDateField()

    class Meta:
        model = AnnouncementModel
        fields = ('id', 'title', 'info', 'broadcast_at', 'category', 'approved')


class EventSerializer(MHacksModelSerializer):
    id = CharField(read_only=True)
    start = UnixEpochDateField()
    locations = PrimaryKeyRelatedField(many=True, pk_field=CharField(),
                                       queryset=LocationModel.objects.all().filter(deleted=False))
    duration = DurationInSecondsField()
    category = ChoiceField(choices=EventModel.CATEGORIES)

    class Meta:
        model = EventModel
        fields = ('id', 'name', 'info', 'start', 'duration', 'locations', 'category', 'approved')


class LocationSerializer(MHacksModelSerializer):
    id = CharField(read_only=True)

    class Meta:
        model = LocationModel
        fields = ('id', 'name', 'latitude', 'longitude')


class MHacksUserSerializer(MHacksModelSerializer):
    id = CharField(read_only=True)

    class Meta:
        model = MHacksUserModel
        fields = ('id', 'first_name', 'last_name', 'email')


class TicketSerializer(MHacksModelSerializer):
    id = CharField(read_only=True)
    creator = MHacksUserSerializer(read_only=True)
    mentor = MHacksUserSerializer(read_only=True)
    title = CharField(required=True)
    description = CharField(required=True)

    _remove_from_request = ('id', 'creator', 'mentor')

    class Meta:
        model = TicketModel
        fields = ('id', 'title', 'description', 'completed', 'creator', 'mentor', 'area')

    # TODO better validation (invalid fields within mentor, check for required fields)
    # TODO raise validation errors when data is invalid
    def run_validation(self, data=None):
        for key in data.keys():
            if key in self._remove_from_request or key not in self.fields:
                data.pop(key)
        return data

    def create(self, validated_data):
        creator = self.context.get('request').user
        ticket = TicketModel.objects.create(creator=creator, **validated_data)
        ticket.save()
        return ticket

    def update(self, instance, validated_data):
        user = self.context.get('request').user
        if instance.creator.id != user.id and not user.is_superuser:
            raise ('You can\'t modify this.')
        for attr, value in validated_data.iteritems():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AuthSerializer(AuthTokenSerializer):
    # Extends auth token serializer to accommodate push notifs

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
