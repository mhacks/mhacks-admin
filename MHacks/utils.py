import logging

import mandrill
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import loader
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from jinja2 import Environment

from config.settings import EMAIL_HOST_USER
from config.settings import MANDRILL_API_KEY


# Sends mail through mandrill client.
def send_mandrill_mail(template_name, subject, email_to, email_vars=None):
    if not email_vars:
        email_vars = dict()

    try:
        MANDRILL_CLIENT = mandrill.Mandrill(MANDRILL_API_KEY)
        message = {
            'subject': subject,
            'from_email': 'hackathon@umich.edu',
            'from_name': 'MHacks',
            'to': [{'email': email_to}],
            'global_merge_vars': []
        }
        for k, v in email_vars.items():
            message['global_merge_vars'].append(
                    {'name': k, 'content': v}
            )
        return MANDRILL_CLIENT.messages.send_template(template_name, [], message)
    except mandrill.Error as e:
        logger = logging.getLogger(__name__)
        logger.error('A mandrill error occurred: %s - %s' % (e.__class__, e))
        raise


def send_email(to_email, email_template_name, html_email_template_name, context):

    # Email subject *must not* contain newlines
    subject = ''.join(context['subject'].splitlines())
    body = loader.render_to_string(email_template_name, context)
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
    else:
        html_email = None
    send_mail(subject=subject, message=body, from_email=EMAIL_HOST_USER, recipient_list=[to_email],
              html_message=html_email)


# Turns a relative URL into an absolute URL.
def _get_absolute_url(request, relative_url):
    current_site = get_current_site(request)
    return "{0}://{1}{2}".format(
        request.scheme,
        request.META['HTTP_HOST'],
        relative_url
    )


def send_application_confirmation_email(user, request):
    send_mandrill_mail(
        'application_confirmation',
        'Your MHacks Application Is Submitted',
        user.email
    )


def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    relative_confirmation_url = reverse(
        'mhacks-validate',
        kwargs={'uid':uid, 'token': token}
    )
    email_vars = {
        'confirmation_url': _get_absolute_url(request, relative_confirmation_url)
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
        kwargs={'uid':uid, 'token': token}
    )
    email_vars = {
        'update_password_url': _get_absolute_url(request, update_password_url)
    }
    send_mandrill_mail(
        'password_reset_instructions',
        'Reset Your MHacks Password',
        user.email,
        email_vars
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
    if query not in data:
        raise forms.ValidationError('Please enter a valid {} url'.format(query))


class ArrayFieldSelectMultiple(forms.SelectMultiple):
    """This is a Form Widget for use with a Postgres ArrayField. It implements
    a multi-select interface that can be given a set of `choices`.

    You can provide a `delimiter` keyword argument to specify the delimeter used.

    """

    def __init__(self, *args, **kwargs):
        # Accept a `delimiter` argument, and grab it (defaulting to a comma)
        self.delimiter = kwargs.pop("delimiter", ",")
        super(ArrayFieldSelectMultiple, self).__init__(*args, **kwargs)

    def render_options(self, choices, value):
        # value *should* be a list, but it might be a delimited string.
        if isinstance(value, str):  # python 2 users may need to use basestring instead of str
            value = value.split(self.delimiter)
        return super(ArrayFieldSelectMultiple, self).render_options(choices, value)

    def value_from_datadict(self, data, files, name):
        from django.utils.datastructures import MultiValueDict
        if isinstance(data, MultiValueDict):
            # Normally, we'd want a list here, which is what we get from the
            # SelectMultiple superclass, but the SimpleArrayField expects to
            # get a delimited string, so we're doing a little extra work.
            return self.delimiter.join(data.getlist(name))
        return data.get(name, None)