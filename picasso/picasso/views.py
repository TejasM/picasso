import json
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.template.loader import get_template
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


def hash_listing(request, hash_key):
    if request.method == "GET":
        try:
            listing = Listing.objects.get(hash_key=hash_key)
            if request.user.is_authenticated():
                try:
                    Review.objects.get(user=request.user, listing=listing)
                    context = {'listing': listing, 'reviewed': True}
                except Review.DoesNotExist:
                    context = {'listing': listing}
                except Review.MultipleObjectsReturned:
                    context = {'listing': listing, 'reviewed': True}
                if listing.owner is None:
                    listing.owner = request.user
                    listing.save()
            else:
                context = {'listing': listing, 'claimable': True}
            return render(request, 'index/individual_listing.html', context)
        except Listing.DoesNotExist:
            return render(request, '404.html')


def send_claim_email(request, list_id):
    # TODO create email
    if request.method == "POST":
        listing = Listing.objects.get(pk=list_id)
        if listing.email != '':
            t = get_template('emails/claim_email.html')
            context = RequestContext(request, {'listing': listing})
            content = t.render(context)
            msg = EmailMessage('Picasso - Claim your business', content, 'contact@findpicasso.com', [listing.email])
            msg.send()
            return HttpResponse(json.dumps({'fail': False}), content_type='application/json')
        else:
            return HttpResponse(json.dumps({'fail': True}), content_type='application/json')
    return HttpResponse("")


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