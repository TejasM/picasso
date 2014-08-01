from django.core.urlresolvers import reverse

__author__ = 'tmehta'
from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import redirect
from social.exceptions import AuthCanceled


class SocialAuthExceptionMiddlewareCustom(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthCanceled:
            return redirect(reverse('index'))
        else:
            pass