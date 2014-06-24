from django.shortcuts import render
from picasso.index.models import Listing, Review

__author__ = 'tmehta'


def individual_listing(request, list_name):
    if request.method == "GET":
        listing = Listing.objects.get(unique_url=list_name)
        if request.user.is_authenticated():
            try:
                Review.objects.get(user=request.user, listing=listing)
                context = {'listing': listing, 'reviewed': True}
            except Review.DoesNotExist:
                context = {'listing': listing}
            except Review.MultipleObjectsReturned:
                context = {'listing': listing, 'reviewed': True}
        else:
            context = {'listing': listing}
        return render(request, 'index/individual_listing.html', context)