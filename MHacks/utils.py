import logging
import sys

import mandrill
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from jinja2 import Environment
from rest_framework import serializers
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import exception_handler

from MHacks.globals import permissions_map
from config.settings import MANDRILL_API_KEY


# Updates permissions to groups
def add_permissions(**kwargs):
    from django.contrib.auth.models import Group, Permission
    groups_queryset = Group.objects.all()
    permissions_queryset = Permission.objects.all()

    # Not the cleanest way but yolo. Maybe use sets? Would make permission removal easier too
    for group_enum, group_permissions in permissions_map.iteritems():
        print('')
        group, created = groups_queryset.get_or_create(name=group_enum)
        if created:
            print('Created group {}.'.format(group_enum))

        group.permissions.clear()
        for permission in group_permissions:
            permission_object = permissions_queryset.filter(codename=permission)
            if not permission_object:
                raise Exception('Invalid permission {}. '
                                'Have all the relevant migrations been applied?'.format(permission))
            permission_object = permission_object[0]

            group.permissions.add(permission_object)
            print('Added permission {} for group {}.'.format(permission, group_enum))

        group.save()


# Sends mail through mandrill client.
def send_mandrill_mail(template_name, subject, email_to, email_vars=None, attachments=None, images=None):
    if not email_vars:
        email_vars = dict()

    from config.settings import DEBUG

    if DEBUG:
        if 'confirmation_url' in email_vars:
            print("Open this URL in a browser: " + email_vars['confirmation_url'])
            sys.stdout.flush()
        return

    try:
        mandrill_client = mandrill.Mandrill(MANDRILL_API_KEY)
        message = {
            'subject': subject,
            'from_email': 'hackathon@umich.edu',
            'from_name': 'MHacks',
            'to': [{'email': email_to}],
            'global_merge_vars': []
        }
        if attachments:
            message['attachments'] = attachments
        if images:
            message['images'] = images
        for k, v in email_vars.items():
            message['global_merge_vars'].append(
                {'name': k, 'content': v}
            )
        return mandrill_client.messages.send_template(template_name, [], message)
    except mandrill.Error as e:
        logger = logging.getLogger(__name__)
        logger.error('A mandrill error occurred: %s - %s' % (e.__class__, e))
        print('A mandrill error occurred: %s - %s' % (e.__class__, e))
        raise


# Turns a relative URL into an absolute URL.
def _get_absolute_url(request, relative_url):
    return "{0}://{1}{2}".format(
        request.scheme,
        request.get_host(),
        relative_url
    )


def send_application_confirmation_email(user):
    send_mandrill_mail(
        'application_submission',
        'Your MHacks Application Is Submitted',
        email_to=user.email,
        email_vars={'FIRST_NAME': user.first_name}
    )


def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    relative_confirmation_url = reverse(
        'mhacks-validate',
        kwargs={'uid': uid, 'token': token}
    )
    email_vars = {
        'confirmation_url': _get_absolute_url(request, relative_confirmation_url),
        'FIRST_NAME': user.first_name
    }
    send_mandrill_mail(
        'confirmation_instructions',
        'Confirm Your Email for MHacks',
        user.email,
        email_vars
    )


def send_password_reset_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    update_password_url = reverse(
        'mhacks-update_password',
        kwargs={'uid': uid, 'token': token}
    )
    send_mandrill_mail(
        'change_password',
        'Reset Your MHacks Password',
        user.email,
        email_vars={
            'update_password_url': _get_absolute_url(request, update_password_url)
        }
    )


def validate_signed_token(uid, token, require_token=True):
    """
    Validates a signed token and uid and returns the user who owns it.
    :param uid: The uid of the request
    :param token: The signed token of the request if one exists
    :param require_token: Whether or not there is a signed token, the token parameter is ignored if False

    :return: The user who's token it is, if one exists, None otherwise
    """
    user_model = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uid))
        user = user_model.objects.get(pk=uid)
        if require_token:
            if user is not None and default_token_generator.check_token(user, token):
                return user
        else:
            return user
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        pass
    return None


def user_belongs_to_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


def environment(**options):
    """
    Hack to inject into Jinja templates so that they are actually usable
    Using Jinja, though, gives us great power and great performance!
    """
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url_for': reverse,
    })
    from django.utils.text import slugify
    env.filters['slugify'] = slugify
    env.filters['belongs_to'] = user_belongs_to_group
    return env


def validate_url(data, query):
    """
    Checks if the given url contains the specified query. Used for custom url validation in the ModelForms
    :param data: full url
    :param query: string to search within the url
    :return:
    """
    if data and query not in data:
        raise forms.ValidationError('Please enter a valid {} url'.format(query))


class GenericListCreateModel(CreateAPIView, ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

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

    # noinspection PyProtectedMember
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
        request_data = request.data.copy()
        request_data['approved'] = request.user.has_perm('%(app_label)s.change_%(model_name)s' %
                                                         {'app_label': model_class._meta.app_label,
                                                          'model_name': model_class._meta.model_name})
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class GenericUpdateDestroyModel(RetrieveUpdateDestroyAPIView):
    permission_classes = (DjangoModelPermissions,)
    lookup_field = 'id'


def serialized_user(user):
    return {'name': user.get_full_name(), 'email': user.email,
            'school': user.cleaned_school_name(),
            'can_post_announcements': user.has_perm('MHacks.add_announcement'),
            'can_edit_announcements': user.has_perm('MHacks.change_announcement'),
            'can_perform_scan': user.has_perm('MHacks.can_perform_scan')}


def mhacks_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if not response:
        return response
    if isinstance(response.data, str):
        response.data = {'detail': response}
    elif isinstance(response.data, list):
        response.data = {'detail': response.data[0]}
    elif not response.data.get('detail', None):
        if len(response.data) == 0:
            response.data = {'detail': 'Unknown error'}
        elif isinstance(response.data, list):
            response.data = {'detail': response.data[0]}
        elif isinstance(response.data, dict):
            first_key = response.data.keys()[0]
            detail_for_key = response.data[first_key]
            if isinstance(detail_for_key, list):
                detail_for_key = detail_for_key[0]
            if first_key.lower() == 'non_field_errors':
                response.data = {'detail': "{}".format(detail_for_key)}
            else:
                response.data = {'detail': "{}: {}".format(first_key.title(), detail_for_key)}
        else:
            response.data = {'detail': 'Unknown error'}
    return response


class UnixEpochDateField(serializers.DateTimeField):
    def to_internal_value(self, value):
        from datetime import datetime
        from pytz import utc
        try:
            return datetime.utcfromtimestamp(float(value)).replace(tzinfo=utc)
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


class NonNullPrimaryKeyField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        if not value:
            return None
        return super(NonNullPrimaryKeyField, self).to_representation(value)


def parse_date_last_updated(request):
    date_last_updated_raw = request.query_params.get('since', None)
    if date_last_updated_raw:
        try:
            from pytz import utc
            from datetime import datetime
            return datetime.utcfromtimestamp(float(date_last_updated_raw)).replace(tzinfo=utc)
        except ValueError:
            print('Value error')
            pass
    return None


def now_as_utc_epoch():
    import pytz
    from datetime import datetime
    return to_utc_epoch(datetime.now(pytz.utc))


def to_utc_epoch(date_time):
    from datetime import datetime

    if isinstance(date_time, datetime):
        import pytz
        date_time = date_time.astimezone(pytz.utc)
        from calendar import timegm
        return timegm(date_time.timetuple())
    return None
