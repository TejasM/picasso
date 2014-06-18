from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext

from picasso.index.models import Listing, Tag


def featured(request):
    if request.method == "GET":
        featured_listings = Listing.objects.order_by('?')[:6]
        context = {'listings': featured_listings}
        return render(request, 'index/featured_listings.html', context)


def get_listings(request):
    if request.method == "GET":
        search = request.GET.get('term', '')
        possible_tags = Tag.objects.filter(tag_name__contains=search).values_list('id', flat=True)
        listings = Listing.objects.filter(listing_name__contains=search) | Listing.objects.filter(
            description__contains=search) | Listing.objects.filter(tags__in=possible_tags)
        context = {'listings': listings}
        return render(request, 'index/listings.html', context)


def add_listing(request):
    if request.method == "POST":
        listing_name = request.POST['listing_name']
        description = request.POST['description']
        listing = Listing.objects.create(listing_name=listing_name, description=description)
        return HttpResponse({'listing': listing.id}, content_type='application/json')


def detail_listing(request, list_id):
    if request.method == "GET":
        listing = Listing.objects.get(pk=int(list_id))
        context = {'listing': listing}
        return render(request, 'index/listing.html', context)


def get_listing(request, list_id):
    if request.method == "GET":
        listings = Listing.objects.filter(id=int(list_id))
        context = {'listings': listings}
        return render(request, 'index/listings.html', context)