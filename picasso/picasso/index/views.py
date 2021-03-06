import json
import logging

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.gis import geos
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError, DataError
from django.db.models import Q, Count
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import RequestContext, Context
from django.template.loader import get_template
import watson

from pygeocoder import Geocoder
from picasso.index.models import Listing, Review


logger = logging.getLogger(__name__)


def featured(request):
    if request.method == "GET":
        featured_listings = Listing.objects.filter(~Q(address=None)).filter(
            ~Q(address__point=None)).filter(~Q(listing_name__contains='Test')).filter(
            ~Q(listing_name__contains='test')).filter(~Q(listing_name__contains='Tejas')).filter(
            ~Q(listing_name__contains='Cheng')).filter(~Q(listing_name__contains='tejas')).filter(
            ~Q(listing_name__contains='Albert'))
        featured_listings = featured_listings.filter(~Q(owner=None) |
                                                     ~Q(review=None))
        featured_listings = featured_listings.order_by('?')[:6]
        context = {'listings': featured_listings, 'title': 'Featured Listings', 'button_name': 'Read More',
                   'categories': True}
        context = RequestContext(request, context)
        t = get_template('index/listings.html')
        lons = [x.address.point.x for x in featured_listings]
        lats = [x.address.point.y for x in featured_listings]
        names = [str(x.listing_name.encode('utf-8')) for x in featured_listings]
        return HttpResponse(
            json.dumps({'html': t.render(context),
                        'lons': str(lons), 'lats': str(lats), 'names': names}),
            content_type='application/json')


def get_listings(request):
    if request.method == "GET":
        original_search = request.GET.get('term', '')
        logger.debug('Search ' + original_search)
        order_by = request.GET.get('order_by', '')
        try:
            location = original_search.split('----')[1]
        except IndexError:
            location = 'Toronto'
        search = original_search.split('----')[0]
        listings = watson.filter(Listing, search).distinct()
        try:
            results = Geocoder.geocode(str(location + ' Canada'))
            lat, lon = results[0].coordinates
            current_point = geos.fromstr("POINT(%s %s)" % (lon, lat))
            if order_by == '':
                temp_listings = listings.filter(~Q(address=None)).filter(~Q(address__point=None)).distance(
                    current_point,
                    field_name='address__point').order_by('distance')
                # extra(
                #select={'factor': '0.01*(inner_point::distance + total_rating)'}).order_by(
                #'factor')
            else:
                temp_listings = listings.filter(~Q(address=None)).filter(~Q(address__point=None)).distance(
                    current_point, field_name='address__point')
            if temp_listings.count() == 0:
                raise Exception
            else:
                listings = temp_listings
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
            lons = [x.address.point.x for x in listings]
            lats = [x.address.point.y for x in listings]
        except Exception as e:
            logger.debug(e)
            lats = []
            lons = []
            if listings.count() != 0:
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
        context = {'listings': listings, 'title': 'Listings', 'button_name': 'Read More', 'filters': True,
                   'term': original_search, 'order_by': order_by}
        context = RequestContext(request, context)
        t = get_template('index/listings.html')
        names = [str(x.listing_name.encode('utf-8')) for x in listings]
        return HttpResponse(
            json.dumps({'html': t.render(context),
                        'lons': str(lons), 'lats': str(lats), 'names': names}),
            content_type='application/json')


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
            claim = request.POST.get('claim-id', '')
            key = request.session.get('key', '')
            try:
                user = User.objects.create(first_name=first_name, last_name=last_name, email=username,
                                           username=username)
                user.set_password(password)
                user.save()
                user = authenticate(username=username, password=password)
                if claim != '':
                    try:
                        l = Listing.objects.get(pk=int(claim))
                        l.visible = True
                        logger.debug("Listing " + l.listing_name + " was claimed")
                        t = get_template('emails/confirm_claim_email.html')
                        context = Context({'listing': l})
                        content_email = t.render(context)
                        msg = EmailMessage('Picasso - Thank You', content_email, 'contact@findpicasso.com',
                                           [l.email])
                        msg.content_subtype = "html"
                        msg.send()
                        l.owner = user
                        l.save()
                    except Listing.DoesNotExist:
                        pass
                if key != '':
                    try:
                        l = Listing.objects.get(pk=int(key))
                        l.visible = True
                        logger.debug("Listing " + l.listing_name + " was claimed")
                        t = get_template('emails/confirm_claim_email.html')
                        context = RequestContext(request, {'listing': l})
                        content_email = t.render(context)
                        msg = EmailMessage('Picasso - Thank You', content_email, 'contact@findpicasso.com',
                                           [l.email])
                        msg.content_subtype = "html"
                        msg.send()
                        l.owner = user
                        l.save()
                    except Listing.DoesNotExist:
                        pass
                    del request.session['sign_up']
                    del request.session['key']
                    request.session.modified = True
                login(request, user)
                return HttpResponse(json.dumps({'success': 1}),
                                    content_type='application/json')
            except IntegrityError:
                return HttpResponse(json.dumps({'success': 0, 'error': 'Username is taken'}),
                                    content_type='application/json')
            except DataError:
                return HttpResponse(json.dumps({'success': 0, 'error': 'Username/Password is too long'}),
                                    content_type='application/json')
        else:
            username = request.POST['email']
            password = request.POST['password']
            claim = request.POST.get('claim-id', '')
            key = request.session.get('key', '')
            try:
                User.objects.get(email=username, username=username)
            except User.DoesNotExist:
                return HttpResponse(json.dumps({'success': 0, 'error': 'Incorrect Username/Password'}),
                                    content_type='application/json')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    if claim != '':
                        try:
                            l = Listing.objects.get(pk=int(claim))
                            l.visible = True
                            logger.debug("Listing " + l.listing_name + " was claimed")
                            t = get_template('emails/confirm_claim_email.html')
                            context = RequestContext(request, {'listing': l})
                            content_email = t.render(context)
                            msg = EmailMessage('Picasso - Thank You', content_email, 'contact@findpicasso.com',
                                               [l.email])
                            msg.content_subtype = "html"
                            msg.send()
                            l.owner = user
                            l.save()
                        except Listing.DoesNotExist:
                            pass
                    if key != '':
                        try:
                            l = Listing.objects.get(pk=int(key))
                            l.visible = True
                            logger.debug("Listing " + l.listing_name + " was claimed")
                            t = get_template('emails/confirm_claim_email.html')
                            context = RequestContext(request, {'listing': l})
                            content_email = t.render(context)
                            msg = EmailMessage('Picasso - Thank You', content_email, 'contact@findpicasso.com',
                                               [l.email])
                            msg.content_subtype = "html"
                            msg.send()
                            l.owner = user
                            l.save()
                        except Listing.DoesNotExist:
                            pass
                        del request.session['sign_up']
                        del request.session['key']
                        request.session.modified = True
                    login(request, user)
                    return HttpResponse(json.dumps({'success': 1}),
                                        content_type='application/json')
            return HttpResponse(json.dumps({'success': 0, 'error': 'Incorrect Username/Password'}),
                                content_type='application/json')
    return render(request, 'base.html')


@login_required
def review_listing(request, list_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=int(list_id))
        comment = request.POST['comment']
        rating = request.POST['rating']
        r = Review.objects.create(comment=comment, rating=rating, user=request.user, listing=listing)
        context = {'review': r, 'count': listing.review_set.count()}
        return render(request, 'index/review.html', context)


@login_required
def edit_review_listing(request, review_id):
    if request.method == "POST":
        r = Review.objects.get(pk=int(review_id))
        r.comment = request.POST['comment']
        r.rating = request.POST['rating']
        r.save()
        context = {'review': r, 'count': r.listing.review_set.count()}
        return render(request, 'index/review.html', context)
    else:
        r = Review.objects.get(pk=int(review_id))
        context = {'review': r, 'count': r.listing.review_set.count()}
        return render(request, 'index/edit-review.html', context)


def contact(request):
    if request.method == "POST":
        message = request.POST.get('comment', '')
        email = request.POST.get('email', '')
        if email != '' and message != '':
            if len(message) > 10:
                subject = message[:10]
            else:
                subject = message
            msg = EmailMessage(subject, email + '\n' + message, 'contact@findpicasso.com', ['contact@findpicasso.com'])
            msg.send()
        return HttpResponse(json.dumps({}), content_type='application/json')
    return HttpResponse(json.dumps({}), content_type='application/json')


def internal_stats(request):
    claimed = Listing.objects.filter(~Q(created_by=None) | ~Q(owner=None)).count()
    reviews = Review.objects.count()
    return render(request, 'internal_stats.html', {'claimed': claimed, 'reviews': reviews})


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


def promotion(request):
    return render(request, 'promotion.html')


def content(request):
    return render(request, 'content.html')