from django.conf.urls import patterns, url
from django.http import HttpResponse

import views


__author__ = 'tmehta'
urlpatterns = patterns('',
                       url(r'^logout$', views.user_logout, name='logout'),
                       url(r'^about$', views.about, name='about'),
                       url(r'^featured$', views.featured, name='featured'),
                       url(r'^get-listings$', views.get_listings, name='get_listings'),
                       url(r'^get-listing/(?P<list_id>\w+)$', views.get_listing, name='get_listing'),
                       url(r'^detail-listing/(?P<list_id>\w+)$', views.detail_listing, name='detail_listing'),
                       url(r'^sign-in/$', views.signin, name='signup'),
                       url(r'^review-listing/(?P<list_id>\w+)/$', views.review_listing, name='review_listing'),
)