import json

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.gis import geos
from django.core import serializers
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from django.template.loader import get_template
from pygeocoder import Geocoder
import watson

from picasso.index.models import Listing, Review


def featured(request):
    if request.method == "GET":
        featured_listings = Listing.objects.filter(~Q(address=None)).filter(~Q(address__point=None)).order_by('?')[:6]
        context = {'listings': featured_listings, 'title': 'Feature Listings', 'button_name': 'Read More'}
        context = RequestContext(request, context)
        t = get_template('index/listings.html')
        lons = [x.address.point.x for x in featured_listings]
        lats = [x.address.point.y for x in featured_listings]
        names = [str(x) for x in featured_listings.values_list('listing_name', flat=True)]
        return HttpResponse(
            json.dumps({'html': t.render(context),
                        'lons': str(lons), 'lats': str(lats), 'names': names}),
            content_type='application/json')


def get_listings(request):
    if request.method == "GET":
        search = request.GET.get('term', '')
        location = search.split('----')[1]
        search = search.split('----')[0]
        listings = watson.filter(Listing, search)
        try:
            results = Geocoder.geocode(str(location + ' Canada'))
            lat, lon = results[0].coordinates
            current_point = geos.fromstr("POINT(%s %s)" % (lon, lat))
            listings = listings.distance(current_point, field_name='address__point').order_by('distance')
            context = {'listings': listings, 'title': 'Listings', 'button_name': 'Read More'}
            return render(request, 'index/listings.html', context)
        except Geocoder:
            context = {'listings': listings, 'title': 'Listings', 'button_name': 'Read More'}
            return render(request, 'index/listings.html', context)


def detail_listing(request, list_id):
    if request.method == "GET":
        listing = Listing.objects.get(pk=int(list_id))
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
        return render(request, 'index/listing.html', context)


def get_listing(request, list_id):
    if request.method == "GET":
        listing = Listing.objects.get(id=int(list_id))
        context = {'l': listing, 'button_name': 'View'}
        return render(request, 'index/single-listing.html', context)


def signin(request):
    if request.method == "POST":
        if request.POST['type'] == "sign-up":
            first_name = request.POST['first-name']
            last_name = request.POST['last-name']
            username = request.POST['email']
            password = request.POST['password']
            try:
                user = User.objects.create(first_name=first_name, last_name=last_name, email=username,
                                           username=username)
                user.set_password(password)
                user.save()
                user = authenticate(username=username, password=password)
                login(request, user)
                return HttpResponse(json.dumps({'success': 1}),
                                    content_type='application/json')
            except IntegrityError:
                return HttpResponse(json.dumps({'success': 0, 'error': 'Username is taken'}),
                                    content_type='application/json')
        else:
            username = request.POST['email']
            password = request.POST['password']
            try:
                User.objects.get(email=username, username=username)
            except User.DoesNotExist:
                return HttpResponse(json.dumps({'success': 0, 'error': 'Incorrect Username/Password'}),
                                    content_type='application/json')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse(json.dumps({'success': 1}),
                                        content_type='application/json')
            return HttpResponse(json.dumps({'success': 0, 'error': 'Incorrect Username/Password'}),
                                content_type='application/json')


@login_required
def review_listing(request, list_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=int(list_id))
        comment = request.POST['comment']
        rating = request.POST['rating']
        r = Review.objects.create(comment=comment, rating=rating, user=request.user, listing=listing)
        context = {'review': r, 'count': listing.review_set.count()}
        return render(request, 'index/review.html', context)


@login_required()
def user_logout(request):
    logout(request)
    return redirect('/')


def about(request):
    return render(request, 'about.html')


def privacy(request):
    return render(request, 'privacy.html')


def terms(request):
    return render(request, 'terms.html')


def content(request):
    return render(request, 'content.html')