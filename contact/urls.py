from django.conf.urls import patterns, url
from django.views.generic.simple import direct_to_template

from .views import contact

urlpatterns = patterns('contact.views',
                       url(r'^$', 'contact', name='contact_form'),
                       url(r'^thanks/$', direct_to_template, {
                           'template': 'contact/thanks.html'
                           }),
                       )