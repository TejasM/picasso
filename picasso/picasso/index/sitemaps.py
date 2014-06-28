from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from picasso.index.models import Listing


class ListingSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Listing.objects.all()

    def lastmod(self, obj):
        return obj.last_modified


class StaticViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 1

    def items(self):
        return ['index', 'main:about', 'main:privacy', 'main:terms', 'main:content']

    def location(self, item):
        return reverse(item)