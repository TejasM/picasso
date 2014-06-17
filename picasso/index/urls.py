from django.conf.urls import patterns, url
from index import views

__author__ = 'tmehta'
urlpatterns = patterns('',
                       url(r'^$', views.featured, name='featured'),
                       url(r'^get-listings$', views.get_listings, name='get_listings'),
                       url(r'^get-listing/(?P<list_id>\w+)$', views.get_listing, name='get_listing'),
                       url(r'^add-listing/$', views.add_listing, name='add_listing'),
                       url(r'^detail-listing/(?P<list_id>\w+)$', views.detail_listing, name='detail_listing'),
)