import datetime
import os

import mailchimp
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.http import (HttpResponseBadRequest, HttpResponseNotAllowed,
                         HttpResponseForbidden)
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, smart_str
from django.utils.http import urlsafe_base64_encode, is_safe_url
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token

from MHacks.decorator import anonymous_required, application_reader_required
from MHacks.forms import RegisterForm, LoginForm, ApplicationForm, ApplicationSearchForm, RegistrationForm, \
    SponsorPortalForm
from MHacks.models import Application, MentorApplication, Registration
from MHacks.pass_creator import create_apple_pass
from MHacks.utils import send_verification_email, send_password_reset_email, validate_signed_token, \
    send_application_confirmation_email, send_registration_email
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
        except Exception:
            return render(request, 'blackout.html', {
                'error': 'Looks like there\'s been an error registering you. Try again or email us at hackathon@umich.edu'})
        return render(request, 'blackout.html', {'success': True})
    elif request.method == 'GET':
        return render(request, 'blackout.html', {})
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])


def index(request):
    return render(request, 'index.html')


def thanks_registering(request):
    return render(request, 'thanks_registering.html')

@login_required()
@permission_required('MHacks.add_application')
@permission_required('MHacks.change_application')
def application(request):
    return render(request, 'applications_closed.html')

    # find the user's application if it exists
    try:
        app = Application.objects.get(user=request.user, deleted=False)
    except Application.DoesNotExist:
        app = None

    if request.method == 'GET':
        form = ApplicationForm(instance=app, user=request.user)
    elif request.method == 'POST':
        if not app:
            try:
                # look for deleted apps too
                app = Application.objects.get(user=request.user)
            except Application.DoesNotExist:
                app = None

        form = ApplicationForm(data=request.POST, files=request.FILES, instance=app, user=request.user)

        if form.is_valid():
            # save application
            app = form.save(commit=False)
            app.user = request.user
            app.submitted = True
            app.deleted = False
            send_application_confirmation_email(request.user)

            # save the app regardless
            app.save()

            return redirect(reverse('mhacks-dashboard'))
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])

    context = {'form': form}
    return render(request, 'application.html', context=context)


@login_required()
def apply_mentor(request):
    return redirect('https://docs.google.com/a/umich.edu/forms/d/e/1FAIpQLSdHtRqgaUORcwkwyOTkOZqDmcXGvPDmfZmEs2G13tbh9gzuBg/viewform')

    # unused as of 9/19/16
    # try:
    #     app = MentorApplication.objects.get(user=request.user, deleted=False)
    # except MentorApplication.DoesNotExist:
    #     app = None
    #
    # if request.method == 'GET':
    #     form = MentorApplicationForm(instance=app)
    # elif request.method == 'POST':
    #     if not app:
    #         try:
    #             # look for deleted apps too
    #             app = MentorApplication.objects.get(user=request.user)
    #         except MentorApplication.DoesNotExist:
    #             app = None
    #
    #     form = MentorApplicationForm(data=request.POST, instance=app)
    #
    #     if form.is_valid():
    #         # save application
    #         app = form.save(commit=False)
    #         app.user = request.user
    #         app.submitted = True
    #         app.deleted = False
    #         app.save()
    #
    #         return redirect(reverse('mhacks-dashboard'))
    # else:
    #     return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])
    #
    # context = {'form': form}
    # return render(request, 'apply_mentor.html', context=context)


@login_required()
def registration(request):
    # Changed to make this work for walk ons
    # make sure the user is has submitted an application & has been accepted
    # try:
    #     hacker_app = Application.objects.get(user=request.user)
    #     if not hacker_app.decision == 'Accept':
    #         return redirect(reverse('mhacks-dashboard'))
    # except Application.DoesNotExist:
    #     return redirect(reverse('mhacks-dashboard'))

    # find the user's application if it exists
    try:
        app = Registration.objects.get(user=request.user, deleted=False)

        if app.submitted:
            return redirect(reverse('mhacks-dashboard'))
    except Registration.DoesNotExist:
        app = None

    if request.method == 'GET':
        form = RegistrationForm(instance=app, user=request.user)
    elif request.method == 'POST':
        if not app:
            try:
                # look for deleted apps too
                app = Registration.objects.get(user=request.user)
            except Registration.DoesNotExist:
                app = None

        form = RegistrationForm(data=request.POST, instance=app, user=request.user)

        if form.is_valid():
            # save application
            app = form.save(commit=False)
            app.user = request.user
            app.submitted = True
            app.deleted = False
            app.save()
            send_registration_email(request.user, request)
            return redirect(reverse('mhacks-dashboard'))
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])

    context = {'form': form}
    return render(request, 'registration.html', context=context)


@anonymous_required
def login(request):
    """
    A lot of this code is identical to the default login code but we have a few hooks (like username query)
    and modifications so we implement it ourselves
    """
    from django.contrib.auth.views import REDIRECT_FIELD_NAME
    redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME, ''))
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
            return redirect(reverse('mhacks-thanks-registering'))
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
            try:
                user = get_user_model().objects.get(email=form.cleaned_data["email"])
            except ObjectDoesNotExist:
                form.errors['email'] = ["No user with that email exists"]
                return render(request, 'password_reset.html', context={'form': form, 'type': reset_type})
            if user:
                send_password_reset_email(user, request)
                return redirect(reverse('mhacks-password_reset_sent'))
    elif request.method == 'GET':
        form = PasswordResetForm()
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])
    if form:
        form.fields['email'].longest = True
    return render(request, 'password_reset.html', context={'form': form, 'type': reset_type})


def password_reset_sent(request):
    return render(request, 'password_reset_sent.html')


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
        from MHacks.pass_creator import create_qr_code_image
        app = request.user.application_or_none()
        registration_app = request.user.registration_or_none()
        qr_code = create_qr_code_image(request.user)
        try:
            mentor_app = MentorApplication.objects.get(user=request.user, deleted=False)
        except MentorApplication.DoesNotExist:
            mentor_app = None

        return render(request, 'dashboard.html', {'groups': groups,
                                                  'application': app,
                                                  'mentor_application': mentor_app,
                                                  'registration_application': registration_app,
                                                  'qr_code': qr_code})

    return HttpResponseNotAllowed(permitted_methods=['GET'])


@login_required
@application_reader_required
def application_search(request):
    if request.method == 'GET':
        form = ApplicationSearchForm()
        context = {'form': form}
        return render(request, 'application_search.html', context=context)

    return HttpResponseNotAllowed(permitted_methods=['GET'])


@login_required
@application_reader_required
def application_review(request):
    if request.method == 'GET':
        event_date = datetime.date(1998, 10, 7)

        search_dict = {}

        hacker_search_keys = {
            'first_name': ['user__first_name', 'istartswith'],
            'last_name': ['user__last_name', 'istartswith'],
            'email': ['user__email', 'icontains'],
            'school': ['school', 'icontains'],
            'major': ['major', 'icontains'],
            'gender': ['gender', 'icontains'],
            'city': ['from_city', 'icontains'],
            'state': ['from_state', 'icontains'],
            'score_min': ['score', 'gte'],
            'score_max': ['score', 'lte'],
        }

        mentor_search_keys = {
            'first_name': ['user__first_name', 'istartswith'],
            'last_name': ['user__last_name', 'istartswith'],
            'email': ['user__email', 'icontains']
        }

        # pick search dict based on which type of search
        search_keys = dict()
        if 'hacker' in request.GET:
            search_keys = hacker_search_keys
        elif 'mentor' in request.GET:
            search_keys = mentor_search_keys

        for key in search_keys:
            if request.GET.get(key):
                condition = "{0}__{1}".format(search_keys[key][0], search_keys[key][1])
                search_dict[condition] = request.GET[key]

        # get the types of applications based on which type of search
        applications = Application.objects.none()
        if 'hacker' in request.GET:
            applications = Application.objects.filter(**search_dict)

            if request.GET.get('is_veteran'):
                applications = applications.filter(num_hackathons__gt=1)

            if request.GET.get('is_beginner'):
                applications = applications.filter(num_hackathons__lt=2)
        elif 'mentor' in request.GET:
            applications = MentorApplication.objects.filter(**search_dict)

        # submitted applications
        applications = applications.filter(submitted=True)

        if request.GET.get('is_non_UM'):
            applications = applications.filter(~Q(user__email__icontains='umich.edu'))

        if request.GET.get('is_minor'):
            applications = applications.filter(birthday__gte=event_date)

        if request.GET.get('decision') and not request.GET.get('decision') == 'All':
            applications = applications.filter(decision=request.GET.get('decision'))

        # from the oldest applicants
        applications = applications.order_by('last_updated')

        if request.GET.get('limit'):
            applications = applications if (int(request.GET['limit']) > len(applications)) else applications[:int(
                request.GET['limit'])]

        applications = applications.filter(deleted=False)
        context = {'results': applications}
        # return the appropriate HTML view
        if 'hacker' in request.GET:
            return render(request, 'application_review.html', context=context)
        elif 'mentor' in request.GET:
            return render(request, 'mentor_review.html', context=context)

    return HttpResponseNotAllowed(permitted_methods=['GET'])


@login_required
@application_reader_required
def update_applications(request):
    if request.method == 'POST':
        id_list = request.POST.getlist('id[]')
        score_list = request.POST.getlist('score[]')
        decision_list = request.POST.getlist('decision[]')
        reimbursement_list = request.POST.getlist('reimbursement[]')

        for i in range(len(id_list)):
            # negative check
            reimbursement_amount = float(reimbursement_list[i])
            reimbursement_amount = reimbursement_amount if reimbursement_amount >= 0 else 0

            if request.POST.get('application_type') == 'hacker':
                Application.objects.filter(id=id_list[i]).update(score=score_list[i],
                                                                 decision=decision_list[i],
                                                                 reimbursement=reimbursement_amount)
            elif request.POST.get('application_type') == 'mentor':
                MentorApplication.objects.filter(id=id_list[i]).update(score=score_list[i],
                                                                       decision=decision_list[i],
                                                                       reimbursement=reimbursement_amount)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def live(request):
    return render(request, 'live.html')


@login_required()
def apple_pass(request):
    response = HttpResponse(content=create_apple_pass(request.user).getvalue(), content_type='application/vnd.apple.pkpass')
    response['MimeType'] = 'application/vnd.apple.pkpass'
    return response


@user_passes_test(lambda u: u.groups.filter(name='sponsor').exists())
def sponsor_portal(request):
    if request.method == 'GET':
        form = SponsorPortalForm()
        context = {'form': form}
        return render(request, 'sponsor_portal.html', context=context)

    return HttpResponseNotAllowed(permitted_methods=['GET'])


@user_passes_test(lambda u: u.groups.filter(name='sponsor').exists())
def sponsor_review(request):
    if request.method == 'GET':
        search_dict = dict()
        search_keys = {
            'first_name': ['user__first_name', 'istartswith'],
            'last_name': ['user__last_name', 'istartswith'],
            'email': ['user__email', 'icontains'],
            'employment': ['employment', 'icontains'],
            'degree': ['degree', 'icontains'],
            'technical_skills': ['technical_skills', 'icontains']
        }

        for key in search_keys:
            if request.GET.get(key):
                if key in ['employment', 'degree', 'technical_skills'] and request.GET.get(key) == 'All':
                    continue
                else:
                    condition = "{0}__{1}".format(search_keys[key][0], search_keys[key][1])
                    search_dict[condition] = request.GET[key]

        results = list()
        registrations = Registration.objects.filter(**search_dict)
        for reg in registrations:
            try:
                hacker_app = Application.objects.get(user=reg.user)
            except Application.DoesNotExist:
                hacker_app = None

            results.append((reg, hacker_app))

        if request.GET.get('education'):
            results = [r for r in results if r[1] and request.GET.get('education') in r[1].school.lower()]

        context = {
            'results': results
        }

        return render(request, 'sponsor_review.html', context=context)

    return HttpResponseNotAllowed(permitted_methods=['GET'])


@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='sponsor').exists())
def resumes(request, filename):
    from config.settings import MEDIA_ROOT

    path = os.path.join(MEDIA_ROOT, filename)
    if os.path.isfile(path):
        response = HttpResponse(content=open(path, "rb"),
                                content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(filename)
        response['X-Sendfile'] = smart_str(path)
        response['Content-Length'] = os.path.getsize(path)
        return response

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
