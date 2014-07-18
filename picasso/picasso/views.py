import json
import logging
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from picasso.index.models import Listing, Review, Tag

__author__ = 'tmehta'

logger = logging.getLogger(__name__)


def individual_listing(request, dash_version, list_name):
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


@csrf_exempt
def send_claim_email(request, list_id):
    # TODO create email
    if request.method == "POST":
        listing = Listing.objects.get(pk=list_id)
        logger.debug('Listing claim sending email to : ' + listing.email)
        if listing.email != '':
            t = get_template('emails/claim_email.html')
            context = RequestContext(request, {'listing': listing})
            content = t.render(context)
            msg = EmailMessage('Picasso - Message for your Business', content, 'contact@findpicasso.com',
                               [listing.email])
            msg.content_subtype = "html"
            msg.send()
            return HttpResponse(json.dumps({'fail': False}), content_type='application/json')
        else:
            return HttpResponse(json.dumps({'fail': True}), content_type='application/json')
    return HttpResponse("")


def category_listings(request, tag_name):
    if request.method == "GET":
        try:
            order_by = request.GET.get('order_by', '')
            if tag_name != "unknown":
                possible_tag = Tag.objects.get(dash_version=tag_name)
                other_tags = Tag.objects.filter(parent_tag=possible_tag)
                list_tags = [possible_tag.id]
                for t in other_tags:
                    list_tags.append(t.id)
                listings = Listing.objects.filter(visible=True).filter(tags__in=list_tags).distinct()
                if order_by != '':
                    listings = listings.annotate(review_count=Count('review')).order_by(order_by)
                paginator = Paginator(listings, 10)
                page = request.GET.get('page')
                try:
                    listings = paginator.page(page)
                except PageNotAnInteger:
                    listings = paginator.page(1)
                except EmptyPage:
                    listings = paginator.page(paginator.num_pages - 1)
                context = {'listings': listings, 'title': possible_tag.tag_name, 'button_name': 'Read More',
                           'sub_categories': other_tags, 'category': possible_tag.tag_name, 'order_by': order_by}
                return render(request, 'index/category_listings.html', context)
            else:
                listings = Listing.objects.filter(tags=None)
                if order_by != '':
                    listings = listings.annotate(review_count=Count('review')).order_by(order_by)
                paginator = Paginator(listings, 10)
                page = request.GET.get('page')
                try:
                    listings = paginator.page(page)
                except PageNotAnInteger:
                    listings = paginator.page(1)
                except EmptyPage:
                    listings = paginator.page(paginator.num_pages)
                context = {'listings': listings, 'title': 'Listings', 'button_name': 'Read More'}
                return render(request, 'index/category_listings.html', context)
        except Tag.DoesNotExist:
            return redirect(reverse('profile:my_reviews'))
    return redirect(reverse('profile:my_reviews'))