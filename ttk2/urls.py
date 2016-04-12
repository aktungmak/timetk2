from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^register/', views.register, name='create_account'),

    url(r'^$', views.activities, name='index'),
    url(r'^activities', views.activities, name='activities'),

    url(r'^netcodes.?$', views.netcodes, name='netcodes'),
    # with these urls, need to make sure that the netcode_id
    # is owned by the logged in user, to prevent spoofing
    url(r'^netcodes/(?P<netcode_id>[0-9]+)/delete', views.delnetcode, name='delnetcode'),
    url(r'^netcodes/(?P<netcode_id>[0-9]+)/toggle', views.togglenetcode, name='togglenetcode'),
    url(r'^netcodes/(?P<netcode_id>[0-9]+)/startstop', views.startstop, name='startstop'),
    url(r'^netcodes/(?P<netcode_id>[0-9]+)/editstart', views.editstart, name='editstart'),

    url(r'^history/(?P<year>\w+)/(?P<month>\w+)/(?P<day>\w+).?$', views.history, name='history'),
    url(r'^history.?$', views.historynow, name='historynow'),

    url(r'^report/(?P<year>\w+)/(?P<month>\w+)/(?P<day>\w+).?$', views.report, name='report'),
    url(r'^report.?$', views.reportnow, name='reportnow'),

    url(r'^events/(?P<event_id>\w+)/edit', views.editevent, name='editevent'),
]