from django.contrib.sitemaps import Sitemap
from picasso.index.models import Listing


class ListingSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Listing.objects.all()

    def lastmod(self, obj):
        return obj.last_modified