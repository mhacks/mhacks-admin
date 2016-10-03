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

    return succeeded, all_fields


def _general_information(user, application=None):
    return [_create_field('NAME', user.get_full_name()),
            _create_field('EMAIL', user.email),
            _create_field('SCHOOL', user.cleaned_school_name(application))]


def error_field(value):
    return _create_field('ERROR', value, color='FF0000')


def _create_field(label, value, color=None):
    return {'label': label,
            'value': value,
            'color': color if color else '000000'}
