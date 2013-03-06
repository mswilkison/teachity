from django.conf.urls import patterns, url

from .views import BidSavedView
from .views import BidUpdateView
from .views import ProjectCreateView
from .views import ProjectDetailView
from .views import ProjectListView
from .views import ProjectUpdateView


urlpatterns = patterns('projects.views',
                       url(r'^view/(?P<pk>\d+)/$', ProjectDetailView.as_view(),
                           name='projects_view_detail'),
                       url(r'^browse/$', ProjectListView.as_view(),
                           name='projects_browse'),
                       url(r'^create/$', ProjectCreateView.as_view(),
                           name='projects_create'),
                       url(r'^edit/(?P<pk>\d+)/$', ProjectUpdateView.as_view(),
                           name='projects_edit'),
                       url(r'^bid/(?P<project_id>\d+)/$', 'create_bid',
                           name='projects_create_bid'),
                       url(r'^bid/saved/(?P<pk>\d+)/$', BidSavedView.as_view(),
                           name='projects_bid_saved'),
                       url(r'^bid/edit/(?P<pk>\d+)/$', BidUpdateView.as_view(),
                           name='projects_bid_edit'),
                       url(r'^classrooms/(?P<project_id>\d+)/$', 'classroom',
                           name='projects_classroom'),
                      )
