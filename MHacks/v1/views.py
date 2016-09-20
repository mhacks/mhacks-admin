from datetime import datetime
from pytz import utc, timezone
import base64

from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

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
    date_updated = datetime(year=2016, month=9, day=16, hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)

    client_updated = parse_date_last_updated(request)
    if client_updated and client_updated >= date_updated:
        return Response(data={'date_updated': now_as_utc_epoch()})

    start_time = datetime(year=2016, month=10, day=8, hour=0, minute=0, second=0, microsecond=0,
                          tzinfo=timezone('US/Eastern'))
    return Response(data={'start_time': to_utc_epoch(start_time),
                          'countdown_duration': 129600,  # 36 hours
                          'hacks_submitted': 118800,  # 33 hours
                          'date_updated': now_as_utc_epoch()})


@api_view(http_method_names=['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def get_map(request):
    """
    Gets the map information
    """
    # FIXME: Implement
    raise ValidationError('Not implemented yet')


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
