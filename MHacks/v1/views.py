from datetime import datetime
from pytz import utc
import base64

from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, BasePermission

from MHacks.models import ScanEvent, ScanEventUser
from MHacks.pass_creator import create_apple_pass
from MHacks.v1.serializers.util import now_as_utc_epoch, parse_date_last_updated, to_utc_epoch
from MHacks.v1.util import serialized_user


@api_view(http_method_names=['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def get_countdown(request):
    """
    Gets the countdown representation for the hackathon
    """
    # Update the date_updated to your current time if you modify the return value of the countdown
    date_updated = datetime(year=2016, month=9, day=22, hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)

    client_updated = parse_date_last_updated(request)
    if client_updated and client_updated >= date_updated:
        return Response(data={'date_updated': now_as_utc_epoch()})

    start_time = datetime(year=2016, month=10, day=8, hour=4, minute=0, second=0, microsecond=0,
                          tzinfo=utc)
    return Response(data={'start_time': to_utc_epoch(start_time),
                          'countdown_duration': 129600,  # 36 hours
                          'hacks_submitted': 118800,  # 33 hours
                          'date_updated': now_as_utc_epoch()})


@api_view(http_method_names=['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def apple_site_association(request):
    return Response(data={"webcredentials": {"apps": ["478C74MJ7T.com.MPowered.MHacks"]}})


@api_view(http_method_names=['GET'])
@permission_classes((IsAuthenticated,))
def apple_pass_endpoint(request):
    return Response(data={"apple_pass": base64.encodestring(create_apple_pass(request.user).getvalue())})


@api_view(http_method_names=['GET'])
@permission_classes((IsAuthenticated,))
def update_user_profile(request):
    return Response(data=serialized_user(request.user))


class CanPerformScan(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.has_perm('MHacks.can_perform_scan')


@api_view(http_method_names=['POST', 'GET'])
@permission_classes((CanPerformScan,))
def perform_scan(request):
    from scan_event import error_field
    if request.method == 'POST':
        information = request.POST
    else:
        information = request.GET

    scan_event_id = information.get('scan_event', None)
    user_id = information.get('user_id', None)
    if not scan_event_id or not user_id:
        raise ValidationError('Invalid fields provided')

    try:
        scan_event = ScanEvent.objects.get(pk=scan_event_id)
        user = get_user_model().objects.get(email=user_id)
    except (ScanEvent.DoesNotExist, get_user_model().DoesNotExist):
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
        import MHacks.v1.scan_event as scan_event_verifiers
        try:
            success, data = getattr(scan_event_verifiers, scan_event.custom_verification)(request, user)
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
