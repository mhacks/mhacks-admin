from config.settings import EMAIL_HOST_USER
from django.template import loader
from django.core.mail import send_mail
from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import get_user_model


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


def _send_email_with_signed_token(user, request, subject, email_template_name, html_email_template_name):
    """
    Create a cryptographically signed token to validate the email or reset password
    We don't need to store it on the backend so its a major win!
    :param user: The user for who needs to verify his/her email
    :param request: The request that generated the need for a verification
    """
    current_site = get_current_site(request)
    context = {
        'email': user.email,
        'domain': current_site.domain,
        'site_name': current_site.name,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'user': user,
        'token': default_token_generator.make_token(user),
        'protocol': request.scheme,
        'subject': subject
    }
    send_email(user.email, email_template_name, html_email_template_name, context)


def send_verification_email(user, request):
    _send_email_with_signed_token(user, request, 'Confirmation Instructions', 'confirm_email.txt', 'confirm_email.html')


def send_password_reset_email(user, request):
    _send_email_with_signed_token(user, request, 'Password Reset Instructions', 'password_reset_email.txt', 'password_reset_email.html')


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
    from globals import groups
    assert group_name in groups.ALL
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
