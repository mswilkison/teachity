from django.conf.urls import patterns, url

from .views import DashboardView
from .views import PublicProfileView


urlpatterns = patterns('users.views',
                       url(r'^edit-profile/$', 'edit_profile', name='users_edit_profile'),
                       url(r'^view-profile/$', 'view_profile', name='users_view_profile'),
                       url(r'^dashboard/$', DashboardView.as_view(),
                           name='users_dashboard'),
                       url(r'^profile/(?P<pk>\d+)/$', PublicProfileView.as_view(),
                           name='users_public_profile'),
                      )
