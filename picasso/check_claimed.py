__author__ = 'tmehta'
from picasso.index.models import Listing
from django.db.models import Q
ls = Listing.objects.filter(~Q(owner=None))
for l in ls:
    print ls.listing_name