from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^activities', views.activities, name='activities'),
    url(r'^netcodes.?$', views.netcodes, name='netcodes'),
    url(r'^netcodes/(?P<netcode_id>[0-9]+)/delete', views.delnetcode, name='delnetcode'),
    url(r'^netcodes/(?P<netcode_id>[0-9]+)/toggle', views.togglenetcode, name='togglenetcode'),
    url(r'^history', views.history, name='history'),
    url(r'^report/(\w+)/(\w+)', views.report, name='report'),
    url(r'^report', views.reportnow, name='reportnow'),
]