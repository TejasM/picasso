from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from index.models import Listing, Tag


def featured(request):
    if request.method == "GET":
        featured_listings = Listing.objects.order_by('?')[:6]
        context = RequestContext(request, {'listings': featured_listings})
        return render('featured_listing.html', context)


def get_listings(request):
    if request.method == "GET":
        search = request.GET.get('term', '')
        possible_tags = Tag.objects.filter(tag_name__contains=search).values_list('id', flat=True)
        listings = Listing.objects.filter(listing_name__contains=search) | Listing.objects.filter(
            description__contains=search) | Listing.objects.filter(tags__in=possible_tags)
        context = RequestContext(request, {'listings': listings})
        return render('listings.html', context)


def add_listing(request):
    if request.method == "POST":
        listing_name = request.POST['listing_name']
        description = request.POST['description']
        listing = Listing.objects.create(listing_name=listing_name, description=description)
        return HttpResponse({'listing': listing.id}, content_type='application/json')


def detail_listing(request, list_id):
    if request.method == "GET":
        listing = Listing.objects.filter(id=int(list_id))
        context = RequestContext(request, {'listing': listing})
        return render('listing.html', context)


def get_listing(request, list_id):
    if request.method == "GET":
        listings = Listing.objects.filter(id=int(list_id))
        context = RequestContext(request, {'listings': listings})
        return render('listings.html', context)