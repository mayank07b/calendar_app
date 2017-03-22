from django.conf.urls import url
from app import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^events/create/$', views.create_event),
    url(r'^events/(?P<pk>[0-9]+)/update/$', views.update_event),
    url(r'^events/(?P<pk>[0-9]+)/delete/$', views.delete_event),
    url(r'^events$', views.fetch_all_events),
    url(r'^month-data$', views.get_month_data),
    url(r'^sync$', views.sync),
]