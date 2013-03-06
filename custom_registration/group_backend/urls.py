"""
URLconf for registration and activation, using a custom django-registration
backend. This backend allows users to choose between the
'tutors' and 'students' groups when they register.

This will also automatically set up the views in
``django.contrib.auth`` at sensible default locations.

"""


from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset
from django.views.generic.simple import direct_to_template

from custom_registration.forms import UsernamePasswordResetForm

from registration.views import activate
from registration.views import register


urlpatterns = patterns('',
                       url(r'^activate/complete/$',
                           direct_to_template,
                           {'template': 'registration/activation_complete.html'},
                           name='registration_activation_complete'),
                       # Activation keys get matched by \w+ instead of the more specific
                       # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
                       # that way it can return a sensible "invalid key" message instead of a
                       # confusing 404.
                       url(r'^activate/(?P<activation_key>\w+)/$',
                           activate,
                           {'backend': 'custom_registration.group_backend.GroupBackend'},
                           name='registration_activate'),
                       url(r'^register/$',
                           register,
                           {'backend': 'custom_registration.group_backend.GroupBackend'},
                           name='registration_register'),
                       url(r'^register/complete/$',
                           direct_to_template,
                           {'template': 'registration/registration_complete.html'},
                           name='registration_complete'),
                       url(r'^register/closed/$',
                           direct_to_template,
                           {'template': 'registration/registration_closed.html'},
                           name='registration_disallowed'),
                       # Overrides default password reset form
                       url(r'^password/reset/$',
                           password_reset,
                           {'password_reset_form': UsernamePasswordResetForm},
                           name='custom_password_reset'),
                       (r'', include('registration.auth_urls')),
                       )
