from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

from dajaxice.core import dajaxice_autodiscover
from dajaxice.core import dajaxice_config

from .views import fetch_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

dajaxice_autodiscover()

urlpatterns = patterns('',
                       (r'^$', direct_to_template, {
                        'template': 'index.html'
                        }),
                       (r'^base/$', direct_to_template, {
                        'template': 'base.html'
                        }),
                       (r'^loggedin/$', direct_to_template, {
                        'template': 'loggedin.html'
                        }),
                       (r'^index/$', direct_to_template, {
                        'template': 'index.html'}, 'index'),
                       (r'^about/$', direct_to_template, {
                        'template': 'about.html'}, 'about'),
                       (r'^faq/$', direct_to_template, {
                        'template': 'faq.html'}, 'faq'),
                       (r'^privacy_policy/$', direct_to_template, {
                        'template': 'privacy-policy.html'}, 'privacy'),
                       (r'^mockups/(?P<template_name>[\w_-]+)/', fetch_template),
                       (r'^accounts/', include('custom_registration.group_backend.urls')),
                       (r'^user/', include('users.urls')),
                       (r'^projects/', include('projects.urls')),
                       (r'^contact/', include('contact.urls')),
                       (r'^stripe/', include('stripe_connect.urls')),
                       (r'^messages/', include('django_messages.urls')),
                       url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    # Examples:
    # url(r'^$', 'teachity.views.home', name='home'),
    # url(r'^teachity/', include('teachity.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

# Serves media files using dev server
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
