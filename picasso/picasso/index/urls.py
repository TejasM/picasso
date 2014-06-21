from django.conf.urls import patterns, url
from django.http import HttpResponse
from django.views.generic import TemplateView

import views


__author__ = 'tmehta'
urlpatterns = patterns('',
                       url(r'^logout$', views.user_logout, name='logout'),
                       url(r'^featured$', views.featured, name='featured'),
                       url(r'^google46c8e47a069f43cd\.html$',
                           lambda r: HttpResponse("google-site-verification: google46c8e47a069f43cd.html",
                                                  mimetype="text/plain")),
                       url(r'^get-listings$', views.get_listings, name='get_listings'),
                       url(r'^get-listing/(?P<list_id>\w+)$', views.get_listing, name='get_listing'),
                       url(r'^add-listing/$', views.add_listing, name='add_listing'),
                       url(r'^detail-listing/(?P<list_id>\w+)$', views.detail_listing, name='detail_listing'),
                       url(r'^sign-in/$', views.signin, name='signup'),
                       url(r'^review-listing/(?P<list_id>\w+)/$', views.review_listing, name='review_listing'),
)