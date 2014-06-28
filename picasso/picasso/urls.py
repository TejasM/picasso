from django.conf.urls import patterns, include, url
from django.conf import settings
from django.http.response import HttpResponse
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from picasso import index
from picasso.index.sitemaps import ListingSitemap
import views
from django.http import HttpResponse
from picasso.index.models import Tag

admin.autodiscover()

sitemaps = {
    'listings': ListingSitemap,
}

urlpatterns = patterns('',
                       url(r'^$', TemplateView.as_view(template_name='base.html')),
                       url(r'^main/', include('picasso.index.urls', namespace='main')),
                       url(r'^user/', include('picasso.profile.urls', namespace='profile')),
                       url(r'^(?P<tag_name>[^/]*)/$', view=views.category_listings),
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
                        url(r'^unknown/(?P<list_name>.*)/$', view=views.individual_listing, name='unknown'))
for t in Tag.objects.all():
    urlpatterns += patterns('',
                            url(r'^' + t.dash_version + '/(?P<list_name>.*)/$', view=views.individual_listing,
                                name=t.dash_version), )
urlpatterns += patterns('',
                        url(r'^admin/', include(admin.site.urls)), )
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
    )
