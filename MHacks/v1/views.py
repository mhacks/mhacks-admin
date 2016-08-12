from datetime import datetime

from django.contrib.staticfiles.templatetags.staticfiles import static
from pytz import utc, timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from serializers import now_as_utc_epoch, parse_date_last_updated, to_utc_epoch


@api_view(http_method_names=['GET'])
def get_countdown(request, *args, **kwargs):
    """
    Gets the countdown representation for the hackathon
    """
    # Update the date_updated to your current time if you modify the return value of the countdown
    date_updated = datetime(year=2016, month=5, day=13, hour=17, minute=20, second=0, microsecond=0, tzinfo=utc)

    client_updated = parse_date_last_updated(request)
    if client_updated and client_updated >= date_updated:
        return Response(data={'date_updated': now_as_utc_epoch()})

    start_time = datetime(year=2016, month=9, day=10, hour=12, minute=0, second=0, microsecond=0,
                          tzinfo=timezone('US/Eastern'))
    return Response(data={'start_time': to_utc_epoch(start_time),
                          'countdown_duration': 129600000,  # 36 hours
                          'hacks_submitted': 118800000,  # 33 hours
                          'date_updated': now_as_utc_epoch()})


@api_view(http_method_names=['GET'])
def get_map(request, *args, **kwargs):
    """
    Gets the map with the pin location for the map and a URL from where to download the map

    Optional parameter low_res: use `True` or `1` if the client cannot handle high resolution images,
        defaults to False when not specified. Use only `0` if you wish to explicitly specify a high resolution.
    """
    # Update the date_updated to your current time if you modify the return value of the countdown
    date_updated = datetime(year=2016, month=5, day=13, hour=17, minute=20, second=0, microsecond=0, tzinfo=utc)

    client_updated = parse_date_last_updated(request)
    if client_updated and client_updated >= date_updated:
        return Response(data={'date_updated': now_as_utc_epoch()})

    try:
        low_resolution_image = bool(int(request.query_params.get('low_res', False)))
    except ValueError:
        low_resolution_image = True

    static_file = 'assets/grand-map@2x.png' if not low_resolution_image else 'assets/grand-map.png'

    return Response(data={'image_url': request.build_absolute_uri(static(static_file)),
                          'south_west_lat': 42.291820, 'south_west_lon': -83.716611,
                          'north_east_lat': 42.293530, 'north_east_lon': -83.713641,
                          'date_updated': now_as_utc_epoch()})
