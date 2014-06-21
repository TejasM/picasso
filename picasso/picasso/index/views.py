import json
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import RequestContext

from picasso.index.models import Listing, Tag, Review


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
        listings = listings.distinct()
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
        listings = Listing.objects.filter(id=int(list_id))
        context = {'listings': listings}
        return render(request, 'index/listings.html', context)


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