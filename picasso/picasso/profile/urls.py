from django.conf.urls import patterns, url
from django.http import HttpResponse

import views


__author__ = 'tmehta'
urlpatterns = patterns('',
                       # listings
                       url(r'^my_listings/$', views.my_listings, name='my_listings'),
                       url(r'^add-listing/$', views.add_listing, name='add_listing'),
                       url(r'^edit-listing/(?P<list_id>\w+)$', views.edit_listing, name='edit_listing'),
                       url(r'^pic-change-listing/(?P<list_id>\w+)$', views.pic_change_listing,
                           name='pic_change_listing'),
                       url(r'^send-contact/(?P<list_id>\w+)$', views.send_contact_email, name='send_contact_email'),

                       # Profile urls
                       url(r'^profile/$', views.profile, name='profile'),
                       url(r'^change_pic/$', views.change_pic, name='change_pic'),
                       url(r'^add-teacher/(?P<list_id>\w+)$', views.add_teacher, name='add_teacher'),

                       # Teachers
                       url(r'^my_teachers/$', views.my_teachers, name='my_teachers'),
                       url(r'^my_reviews/$', views.my_reviews, name='my_reviews'),
)