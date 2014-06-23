import json
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from picasso.index.models import Listing, Address


@login_required
def add_listing(request):
    if request.method == "POST":
        listing_name = request.POST['listing_name']
        description = request.POST['description']
        address = request.POST['address']
        postal = request.POST['postal']
        city = request.POST['city']
        country = request.POST['country']
        phone = request.POST['phone']
        owner = request.POST['owner']
        active = request.POST['active']
        address = Address.objects.create(city=city, country=country, postal_code=postal, location=address)
        if owner:
            listing = Listing.objects.create(listing_name=listing_name, description=description, address=address,
                                             phone=phone, active=active, owner=request.user)
        else:
            listing = Listing.objects.create(listing_name=listing_name, description=description, address=address,
                                             phone=phone, active=active)
        return HttpResponse(json.dumps({'id': listing.id}), content_type='application/json')
    else:
        return render(request, 'profile/create_listing.html')


@login_required
def edit_listing(request, list_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=int(list_id))
        listing.listing_name = request.POST['listing_name']
        listing.description = request.POST['description']
        listing.save()
        return HttpResponse({'listing': listing.id}, content_type='application/json')
    else:
        listing = Listing.objects.get(pk=int(list_id))
        context = {'listing': listing}
        return render(request, 'profile/edit_listing.html', context)


@login_required
def my_listings(request):
    listings = Listing.objects.filter(Q(created_by=request.user) | Q(owner=request.user))
    return render(request, 'my_listings.html', {'listings': listings, 'title': 'My Listings', 'button_name': 'View'})


@login_required
def profile(request):
    return None