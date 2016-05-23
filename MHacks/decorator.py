from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url


def anonymous_required(view_function, redirect_to=None):
    return AnonymousRequired(view_function, redirect_to)


class AnonymousRequired(object):
    def __init__(self, view_function, redirect_to):
        self.view_function = view_function
        self.redirect_to = redirect_to

    def __call__(self, request, *args, **kwargs):
        if request.user is not None and request.user.is_authenticated():
            from django.conf import settings
            return HttpResponseRedirect(resolve_url(self.redirect_to or settings.LOGIN_REDIRECT_URL))
        return self.view_function(request, *args, **kwargs)
