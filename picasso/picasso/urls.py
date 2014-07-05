from django.conf.urls import patterns, include, url
from django.conf import settings
from django.http.response import HttpResponse
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from picasso import index
from picasso.index.sitemaps import ListingSitemap, StaticViewSitemap
import views
from django.http import HttpResponse
from picasso.index.models import Tag
from picasso.index.views import *
from django.views.generic import TemplateView

admin.autodiscover()

sitemaps = {
    'listings': ListingSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = patterns('',
                       url(r'^$', TemplateView.as_view(template_name='base.html'), name='index'),

                       # main
                       url(r'^logout$', user_logout, name='logout'),
                       url(r'^about$', about, name='about'),
                       url(r'^privacy$', privacy, name='privacy'),
                       url(r'^terms$', terms, name='terms'),
                       url(r'^content$', content, name='content'),
                       url(r'^contact$', contact, name='contact'),
                       url(r'^featured$', featured, name='featured'),
                       url(r'^get-listings$', get_listings, name='get_listings'),
                       url(r'^get-listing/(?P<list_id>\w+)$', get_listing, name='get_listing'),
                       url(r'^detail-listing/(?P<list_id>\w+)$', detail_listing, name='detail_listing'),
                       url(r'^sign-in/$', signin, name='signup'),
                       url(r'^review-listing/(?P<list_id>\w+)/$', review_listing, name='review_listing'),

                       # Others
                       url(r'^user/', include('picasso.profile.urls', namespace='profile')),


                       # Emails
                       url(r'claim_account/(?P<list_id>\w+)/$', views.send_claim_email, name='send_claim_email'),

                       # Admin
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^(?P<tag_name>[^/]*)/$', view=views.category_listings),

                       #SEO
                       url(r'^google46c8e47a069f43cd\.html$',
                           lambda r: HttpResponse("google-site-verification: google46c8e47a069f43cd.html",
                                                  mimetype="text/plain")),
                       url(r'^google085706dc2e6c8637\.html$',
                           lambda r: HttpResponse("google-site-verification: google085706dc2e6c8637.html",
                                                  mimetype="text/plain")),
                       url(r'BingSiteAuth\.xml', TemplateView.as_view(template_name='BingSiteAuth.xml')),
                       (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

                       # Examples:
                       # url(r'^$', 'picasso.views.home', name='home'),
                       # url(r'^picasso/', include('picasso.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
)



# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += patterns('',
                        url(r'^unknown/(?P<list_name>.*)/$', view=views.individual_listing, name='unknown'),
                        url(r'^hash-key/(?P<hash_key>[a-zA-z0-9]{40})/$',
                            view=views.hash_listing, name='hash-key'),)
for t in Tag.objects.all():
    urlpatterns += patterns('',
                            url(r'^' + t.dash_version + '/(?P<list_name>.*)/$', view=views.individual_listing,
                                name=t.dash_version), )
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
    )
