from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from picasso.index.models import Listing, Review, Tag

__author__ = 'tmehta'


def individual_listing(request, list_name):
    if request.method == "GET":
        try:
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
        except Listing.DoesNotExist:
            return render(request, '404.html')


def hash_listing(request, list_name, hash_key):
    if request.method == "GET":
        try:
            listing = Listing.objects.get(unique_url=list_name, hash_key=hash_key)
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
            context['claimable'] = True
            return render(request, 'index/individual_listing.html', context)
        except Listing.DoesNotExist:
            return render(request, '404.html')


def category_listings(request, tag_name):
    if request.method == "GET":
        try:
            if tag_name != "unknown":
                possible_tag = Tag.objects.get(dash_version=tag_name)
                listings = Listing.objects.filter(tags__in=[possible_tag.id])
                context = {'listings': listings, 'title': possible_tag.tag_name, 'button_name': 'Read More'}
                return render(request, 'index/category_listings.html', context)
            else:
                listings = Listing.objects.filter(tags=None)
                context = {'listings': listings, 'title': 'Listings', 'button_name': 'Read More'}
                return render(request, 'index/category_listings.html', context)
        except Tag.DoesNotExist:
            return redirect(reverse('profile:my_reviews'))
    return redirect(reverse('profile:my_reviews'))