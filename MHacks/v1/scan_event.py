from rest_framework.exceptions import ValidationError

from MHacks.models import ScanEvent as ScanEventModel, Registration, Application
from MHacks.v1.serializers import ScanEventSerializer
from MHacks.v1.util import GenericListCreateModel, GenericUpdateDestroyModel


class ScanEvents(GenericListCreateModel):
    """
    Announcements are what send push notifications and are useful for pushing updates to MHacks participants.
    Anybody who is logged in can make a GET request where as only authorized users can create, update and delete them.
    """
    serializer_class = ScanEventSerializer
    query_set = ScanEventModel.objects.none()

    def get_queryset(self):
        date_last_updated = super(ScanEvents, self).get_queryset()
        if date_last_updated:
            query_set = ScanEventModel.objects.all().filter(last_updated__gte=date_last_updated)
        else:
            query_set = ScanEventModel.objects.all().filter(deleted=False)

        return query_set


class ScanEvent(GenericUpdateDestroyModel):
    serializer_class = ScanEventSerializer
    queryset = ScanEventModel.objects.all()


# Scan Verifiers
# IMPORTANT NOTE: All scan verifiers must go in this file as a global function, if not
# it will simply not work

def registration_scan_verify(request, scanned_user):
    application = scanned_user.application_or_none()
    registration = scanned_user.registration_or_none()
    if not application or not registration:
        raise ValidationError('No registration found for {}. Register manually'.format(scanned_user.get_short_name()))
    if not registration.acceptance:
        raise ValidationError('{} did not accept registration'.format(scanned_user.get_short_name()))
    all_fields = _general_information(scanned_user, application)
    if application.user_is_minor():
        all_fields.append(_create_field('MINOR', 'Yes', color='FF0000'))
    return all_fields


def general_information_scan_verify(request, scanned_user):
    return _general_information(scanned_user)


def swag_scan_verify(request, scanned_user):
    try:
        registration = Registration.objects.get(user=scanned_user)
    except Registration.DoesNotExist:
        raise ValidationError('No registration found for {}. Register manually'.format(scanned_user.get_short_name()))
    return _general_information(scanned_user) + \
            [_create_field('T-SHIRT SIZE', registration.t_shirt_size, 'tshirt', color='0000FF')]


def meal_scan_verify(request, scanned_user):
    registration = scanned_user.registration_or_none()
    dietary_restrictions = registration.dietary_restrictions if registration and registration.dietary_restrictions else 'None'
    return _general_information(scanned_user) + \
           [_create_field('Dietary Restrictions', dietary_restrictions, 'dietary', '0000FF')]


def _general_information(user, application=None):
    return [_create_field('NAME', user.get_full_name()),
            _create_field('EMAIL', user.email),
            _create_field('SCHOOL', user.cleaned_school_name(application))]


def _create_field(label, value, id_value=None, color=None):
    return {'id': id_value if id_value else label.lower(),
            'label': label,
            'value': value,
            'color': color if color else '000000'}
