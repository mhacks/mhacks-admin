from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from utils import GenericListCreateModel, GenericUpdateDestroyModel, UnixEpochDateField, now_as_utc_epoch, to_utc_epoch
from models import Any, MHacksModelSerializer
from settings import AUTH_USER_MODEL


class ScanEventModel(Any):
    name = models.CharField(max_length=60, unique=True)
    number_of_allowable_scans = models.IntegerField(default=1, validators=[MinValueValidator(limit_value=0)])
    scanned_users = models.ManyToManyField(AUTH_USER_MODEL, related_name="scan_event_users", blank=True, through='ScanEventUser')
    expiry_date = models.DateTimeField(blank=True, null=True)
    custom_verification = models.CharField(blank=True, max_length=255)

    class Meta:
        permissions = (("can_perform_scan", "Can perform a scan"),)

    def __unicode__(self):
        return self.name


class ScanEventSerializer(MHacksModelSerializer):
    id = CharField(read_only=True)
    expiry_date = UnixEpochDateField()

    class Meta:
        model = ScanEventModel
        fields = ('id', 'name', 'expiry_date')


# A custom proxy used for the Many To Many field below
class ScanEventUser(models.Model):
    scan_event = models.ForeignKey(ScanEventModel, on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)

    def __unicode__(self):
        return self.user.get_full_name() + '\'s ' + self.scan_event.name + ' Scan (' + str(self.count) + ')'


class ScanEventAPIView(GenericUpdateDestroyModel):
    serializer_class = ScanEventSerializer
    queryset = ScanEventModel.objects.all()


class ScanEventListAPIView(GenericListCreateModel):
    """
    Announcements are what send push notifications and are useful for pushing updates to MHacks participants.
    Anybody who is logged in can make a GET request where as only authorized users can create, update and delete them.
    """
    serializer_class = ScanEventSerializer
    query_set = ScanEventModel.objects.none()

    def get_queryset(self):
        date_last_updated = super(ScanEventListAPIView, self).get_queryset()
        if date_last_updated:
            query_set = ScanEventModel.objects.all().filter(last_updated__gte=date_last_updated)
        else:
            query_set = ScanEventModel.objects.all().filter(deleted=False)

        return query_set


class CanPerformScan(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.has_perm('MHacks.can_perform_scan')


@api_view(http_method_names=['POST', 'GET'])
@permission_classes((CanPerformScan,))
def perform_scan(request):
    from scan_events import error_field
    if request.method == 'POST':
        information = request.POST
    else:
        information = request.GET

    scan_event_id = information.get('scan_event', None)
    user_id = information.get('user_id', None)
    if not scan_event_id or not user_id:
        raise ValidationError('Invalid fields provided')

    try:
        scan_event = ScanEventModel.objects.get(pk=scan_event_id)
        user = get_user_model().objects.get(email=user_id)
    except (ScanEventModel.DoesNotExist, get_user_model().DoesNotExist):
        raise ValidationError('Invalid scan event or user')

    if scan_event.expiry_date:
        if scan_event.deleted or to_utc_epoch(scan_event.expiry_date) < now_as_utc_epoch():
            raise ValidationError('Scan event is no longer valid')

    successful_scan = True
    error = None
    data = []
    scan_event_user_join = None
    if scan_event.number_of_allowable_scans:
        try:
            scan_event_user_join = ScanEventUser.objects.get(user=user, scan_event=scan_event)
            number_of_scans = scan_event_user_join.count
        except (ScanEventUser.DoesNotExist, get_user_model().DoesNotExist):
            number_of_scans = 0

        if number_of_scans >= scan_event.number_of_allowable_scans:
            successful_scan = False
            error = error_field('Can\'t scan again')

    success = True
    if scan_event.custom_verification:
        try:
            # FIXME: Figure out what to do here...
            success, data = getattr(name=scan_event.custom_verification)(request, user)
        except AttributeError:
            pass  # This shouldn't happen normally but we defensively protect against it
    successful_scan = successful_scan and success
    if error:
        data.append(error)
    scan_result = {'scanned': successful_scan, 'data': data}

    # Only if its a POST request do we actually "do" the scan
    # GET requests are peeks i.e. they don't modify the database at all
    # If there is no number_of_allowable_scans we don't do anything on a POST either (unlimited)
    if successful_scan and scan_event.number_of_allowable_scans and request.method == 'POST':
        if scan_event_user_join:
            scan_event_user_join.count += 1
        else:
            scan_event_user_join = ScanEventUser(user=user, scan_event=scan_event, count=1)
        scan_event_user_join.save()

    return Response(data=scan_result)


# Scan Verifiers
# IMPORTANT NOTE: All scan verifiers must go in this file as a global function, if not
# it will simply not work

def registration_scan_verify(request, scanned_user):
    succeeded = True
    application = scanned_user.application_or_none()
    registration = scanned_user.registration_or_none()
    all_fields = _general_information(scanned_user, application)
    if application and application.user_is_minor():
        all_fields.append(_create_field('MINOR', 'Yes', color='FF0000'))

    if not registration or not registration.acceptance:
        all_fields.append(error_field('Not registered. Send to registration desk.'))
        succeeded = False
    return succeeded, all_fields


def general_information_scan_verify(request, scanned_user):
    return True, _general_information(scanned_user)


def swag_scan_verify(request, scanned_user):
    succeeded = True
    all_fields = [_create_field('NAME', scanned_user.get_full_name())]
    registration = scanned_user.registration_or_none()
    if not registration:
        all_fields.append(error_field('Not registered. Send to registration desk.'))
        succeeded = False
    else:
        all_fields.append(_create_field('T-SHIRT SIZE', registration.t_shirt_size))
    application = scanned_user.application_or_none()
    if application and application.mentoring:
        all_fields.append(_create_field('MENTOR', 'Yes', color='0000FF'))

    return succeeded, all_fields


def _general_information(user, application=None):
    return [_create_field('NAME', user.get_full_name()),
            _create_field('EMAIL', user.email),
            _create_field('SCHOOL', user.cleaned_school_name(application))]


def error_field(value):
    return _create_field('ERROR', value, color='FF0000')


def _create_field(label, value, color='000000'):
    return {'label': label,
            'value': value,
            'color': color}


