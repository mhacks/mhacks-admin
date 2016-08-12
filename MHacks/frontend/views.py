import mailchimp
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.urlresolvers import reverse
from django.http import (HttpResponseBadRequest, HttpResponseNotAllowed,
                         HttpResponseForbidden)
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, is_safe_url
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token

from MHacks.decorator import anonymous_required
from MHacks.forms import RegisterForm, LoginForm, ApplicationForm
from MHacks.models import Application
from MHacks.utils import send_verification_email, send_password_reset_email, validate_signed_token, send_application_confirmation_email
from config.settings import MAILCHIMP_API_KEY, LOGIN_REDIRECT_URL

MAILCHIMP_API = mailchimp.Mailchimp(MAILCHIMP_API_KEY)


def blackout(request):
    if request.method == 'POST':
        if 'email' not in request.POST:
            return HttpResponseBadRequest()
        
        email = request.POST.get("email")
        list_id = "52259aef0d"
        try:
            MAILCHIMP_API.lists.subscribe(list_id, {'email': email}, double_optin=False)
        except mailchimp.ListAlreadySubscribedError:
            return render(request, 'blackout.html', {'error': 'Looks like you\'re already subscribed!'})
        except:
            return render(request, 'blackout.html', {'error': 'Looks like there\'s been an error registering you. Try again or email us at hackathon@umich.edu'})
        return render(request, 'blackout.html', {'success': True})
    elif request.method == 'GET':
        return render(request, 'blackout.html', {})
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])


def index(request):
    return render(request, 'index.html')


@login_required()
@permission_required('MHacks.add_application')
@permission_required('MHacks.change_application')
def application(request):
    # find the user's application if it exists
    try:
        app = Application.objects.get(user=request.user)
    except Application.DoesNotExist:
        app = None

    if request.method == 'GET':
        if app and app.submitted:
            return redirect(reverse('mhacks-dashboard'))

        form = ApplicationForm(instance=app)
    elif request.method == 'POST':
        form = ApplicationForm(data=request.POST, files=request.FILES, instance=app)
        if form.is_valid():
            # save application
            app = form.save(commit=False)
            app.submitted = True
            app.user = request.user
            app.save()

            send_application_confirmation_email(request.user)  # send conf email
            return redirect(reverse('mhacks-dashboard'))
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])

    context = {'form': form}
    return render(request, 'application.html', context=context)


# I just copied the code from apply, not sure if the mentorship form needs anything different -Nevin
def applyMentor(request):
    if request.method == 'GET':
        return render(request, 'applyMentor.html', {})
        pass
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])


@anonymous_required
def login(request):
    """
    A lot of this code is identical to the default login code but we have a few hooks (like username query)
    and modifications so we implement it ourselves
    """
    from django.contrib.auth.views import REDIRECT_FIELD_NAME
    redirect_to = request.POST.get(REDIRECT_FIELD_NAME,
                                   request.GET.get(REDIRECT_FIELD_NAME, ''))
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = reverse(LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return redirect(redirect_to)
    elif request.method == "GET":
        form = LoginForm(request, initial=request.GET)
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])
    context = {
        'form': form,
        REDIRECT_FIELD_NAME: redirect_to,
    }
    return render(request, 'login.html', context)


def logout(request):
    """
    We are nice about logout requests where if we are not logged in we fail silently.
    However, we only accept POST requests for logout, not doing so is a security vulnerability, i.e. CSRF
    attacks will be trivial (although not detrimental for security it can be bothersome to our users if malicious
    users decide to use this attack)
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(permitted_methods=['POST'])
    auth_logout(request)
    return redirect(reverse('mhacks-home'))


@anonymous_required
def register(request):
    user_pk = None
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = get_user_model().objects.create_user(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                request=request
            )
            user.save()
            user_pk = urlsafe_base64_encode(force_bytes(user.pk))
            form = None
    elif request.method == 'GET':
        form = RegisterForm()
    else:
        return HttpResponseNotAllowed(permitted_methods=['POST', 'GET'])
    return render(request, 'register.html', {'form': form, 'user_pk': user_pk})


@anonymous_required
def request_verification_email(request, user_pk):
    user = validate_signed_token(user_pk, None, require_token=False)
    if user is not None:
        send_verification_email(user, request)
    return redirect(reverse('mhacks-login') + '?username=' + user.email)


# CSRF exempt because we need to allow a POST from mobile clients and marking this exempt cannot cause
# any security vulnerabilities since it is @anonymous_required
@csrf_exempt
@anonymous_required
def reset_password(request):
    reset_type = 'reset_request'
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = get_user_model().objects.get(email=form.cleaned_data["email"])
            if user:
                send_password_reset_email(user, request)
                reset_type = 'reset_requested'
                form = None
    elif request.method == 'GET':
        form = PasswordResetForm()
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])
    if form:
        form.fields['email'].longest = True
    return render(request, 'password_reset.html', {'form': form, 'type': reset_type})


@anonymous_required
def validate_email(request, uid, token):
    user = validate_signed_token(uid, token)
    if user is None:
        return HttpResponseForbidden()
    user.email_verified = True
    user.save()
    return redirect(reverse('mhacks-login') + '?username=' + user.email)


@anonymous_required
def update_password(request, uid, token):
    user = validate_signed_token(uid, token)
    if not user:
        return HttpResponseForbidden()  # Just straight up forbid this request, looking fishy already!
    if request.method == 'POST':
        form = SetPasswordForm(user, data=request.POST)
        if form.is_valid():
            form.save()
            Token.objects.filter(user_id__exact=user.pk).delete()
            return redirect(reverse('mhacks-login') + '?username=' + user.email)
    elif request.method == 'GET':
        form = SetPasswordForm(user)
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])
    form.fields['new_password2'].label = 'Confirm New Password'
    form.fields['new_password2'].longest = True
    return render(request, 'password_reset.html', {'form': form, 'type': 'reset', 'uid': uid, 'token': token})


@login_required
def dashboard(request):
    if request.method == 'GET':
        from MHacks.globals import groups
        return render(request, 'dashboard.html', {'groups': groups})
    return HttpResponseNotAllowed(permitted_methods=['GET'])


def live(request):
    return HttpResponseNotAllowed(permitted_methods=[])
