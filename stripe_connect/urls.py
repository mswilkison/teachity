from django.conf.urls import patterns, url

from .views import TransactionCreateView
from .views import TransactionDetailView

urlpatterns = patterns('stripe_connect.views',
                       url(r'^authorize/$', 'oauth_start', name='stripe_authorize'),
                       url(r'^confirmation/$', 'retrieve_token', name='stripe_connect_success'),
                       url(r'^key_exists/$', 'key_exists', name='stripe_key_exists'),
                       url(r'^transaction/(?P<pk>\d+)/$', TransactionDetailView.as_view(),
                           name='stripe_view_transaction'),
                       url(r'^payment/(?P<project_id>\d+)/$', TransactionCreateView.as_view(),
                           name='stripe_handle_payment'),
                      )
