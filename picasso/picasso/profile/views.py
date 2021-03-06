import json
import logging
import re
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import get_template
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from pygeocoder import Geocoder
from pygeolib import GeocoderError

from picasso.index.models import Listing, Address, Tag

# TODO: For all addresses get geocoder
from picasso.profile.models import UserProfile

logger = logging.getLogger(__name__)


def add_listing(request):
    if request.method == "POST":
        listing_name = request.POST['listing_name']
        class_name = request.POST['class_name']
        place_name = request.POST['place_name']
        description = request.POST['description']
        address = request.POST['address']
        postal = request.POST['postal']
        city = request.POST['city']
        email = request.POST['email']
        country = request.POST['country']
        phone = request.POST['phone']
        owner = request.POST['owner']
        site = request.POST['website']
        l_o_e = request.POST.getlist('level_of_expertise')
        categories = request.POST['categories'].split(',')
        tags = []
        for cat in categories:
            cat = cat.strip()
            if cat != '':
                name = re.sub(r'\W+', '-', cat).lower()
                try:
                    tags.append(Tag.objects.get(dash_version=name).id)
                except Tag.DoesNotExist:
                    t = Tag.objects.create(dash_version=name, tag_name=cat)
                    tags.append(t.id)
        if not l_o_e:
            l_o_e = "All"
        else:
            l_o_e = ", ".join(l_o_e)
        price_min = request.POST['price_min']
        price_max = request.POST['price_max']
        active = True if request.POST['active'] == "true" else False
        try:
            results = Geocoder.geocode(str(address + ' ' + postal + ' Canada'))
            lat, lon = results[0].coordinates
        except IndexError:
            lat, lon = 43.7, 79.4
        except GeocoderError:
            lat, lon = 43.7, 79.4
        point = "POINT(%s %s)" % (lon, lat)
        address = Address.objects.create(city=city, country=country, postal_code=postal, location=address, point=point)
        if owner == "true":
            if request.user.is_authenticated():
                owner = request.user
            else:
                owner = None
                request.session['sign_up'] = True
        else:
            owner = None
        if request.user.is_authenticated():
            listing = Listing.objects.create(listing_name=listing_name, description=description, address=address,
                                             phone=phone, active=active, owner=owner, created_by=request.user,
                                             level_of_expertise=l_o_e, price_min=price_min, price_max=price_max,
                                             email=email, website=site, place_name=place_name, class_name=class_name)
        else:
            listing = Listing.objects.create(listing_name=listing_name, description=description, address=address,
                                             phone=phone, active=active, owner=owner,
                                             level_of_expertise=l_o_e, price_min=price_min, price_max=price_max,
                                             email=email, website=site, place_name=place_name, class_name=class_name)
        if request.session.get('sign_up', '') != '':
            if not request.user.is_authenticated():
                request.session['key'] = listing.id
        if settings.DEBUG is False and not tags:
            tags.append(Tag.objects.get(tag_name="Blank"))
        listing.tags = tags
        listing.save()
        return HttpResponse(json.dumps({'id': listing.id, 'url': listing.get_unique_url}),
                            content_type='application/json')
    else:
        return render(request, 'profile/create_listing.html')


@csrf_exempt
@login_required
def add_teacher(request, list_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=list_id)
        request.user.profile.teachers.add(listing)
        return HttpResponse(json.dumps({}), content_type='application/json')


@login_required
def edit_listing(request, list_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=int(list_id))
        listing.listing_name = request.POST['listing_name']
        listing.class_name = request.POST['class_name']
        listing.place_name = request.POST['place_name']
        listing.description = request.POST['description']
        listing.email = request.POST['email']
        listing.website = request.POST['website']
        listing.address.location = request.POST['address']
        listing.address.postal = request.POST['postal']
        listing.address.city = request.POST['city']
        listing.address.country = request.POST['country']
        try:
            results = Geocoder.geocode(str(listing.address.location + ' ' + listing.address.postal + ' Canada'))
            lat, lon = results[0].coordinates
        except IndexError:
            lat, lon = 43.7, 79.4
        except GeocoderError:
            lat, lon = 43.7, 79.4
        point = "POINT(%s %s)" % (lon, lat)
        listing.address.point = point
        listing.address.save()
        listing.phone = request.POST['phone']
        l_o_e = request.POST.getlist('level_of_expertise[]')
        if l_o_e:
            listing.level_of_expertise = ", ".join(l_o_e)
        else:
            listing.level_of_expertise = "All"
        listing.price_min = request.POST['price_min']
        listing.price_max = request.POST['price_max']
        categories = request.POST['categories'].split(',')
        tags = []
        for cat in categories:
            if cat != '':
                cat = cat.strip()
                name = re.sub(r'\W+', '-', cat).lower()
                try:
                    tags.append(Tag.objects.get(dash_version=name).id)
                except Tag.DoesNotExist:
                    tags.append(Tag.objects.create(dash_version=name, tag_name=cat).id)
        if not tags:
            tags.append(Tag.objects.get(tag_name="Blank"))
        listing.tags = tags
        if request.POST['owner'] == "true":
            listing.owner = request.user
        if request.POST['active'] == "true":
            listing.active = True
        else:
            listing.active = False
        listing.last_modified = timezone.now()
        listing.save()
        return HttpResponse(json.dumps({'id': listing.id}), content_type='application/json')
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
    if request.method == "GET":
        try:
            profile_inner = request.user.profile
        except:
            profile_inner = UserProfile.objects.create(user=request.user)
        listings = profile_inner.teachers.all()
        t = get_template('index/listings.html')
        favs = t.render(
            RequestContext(request, {'listings': listings, 'title': 'Favourite Teachers', 'button_name': 'View'}))
        reviews = request.user.review_set.all()
        reviewes = t.render(RequestContext(request, {'reviews': reviews}))
        me_listings = Listing.objects.filter(Q(owner=request.user))
        return render(request, 'profile.html',
                      {'favs': favs, 'reviews': reviewes, 'my_listings': me_listings})
    else:
        user = request.user
        first_name = request.POST['first']
        last_name = request.POST['last']
        email = request.POST['email']
        nick = request.POST['nick']
        location = request.POST['location']
        postal = request.POST['postal']
        city = request.POST['city']
        country = request.POST['country']
        phone = request.POST['phone']
        hobbies = request.POST['hobbies'].split(',')
        tags = []
        for cat in hobbies:
            cat = cat.strip()
            name = re.sub(r'\W+', '-', cat).lower()
            try:
                tags.append(Tag.objects.get(dash_version=name).id)
            except Tag.DoesNotExist:
                tags.append(Tag.objects.create(dash_version=name, tag_name=cat).id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        user.profile.nickname = nick
        if user.profile.address:
            user.profile.address.location = location
            user.profile.address.postal_code = postal
            user.profile.address.city = city
            user.profile.address.country = country
            user.profile.address.save()
        else:
            addr = Address.objects.create(location=location, postal_code=postal, city=city, country=country)
            user.profile.address = addr
        user.profile.phone = phone
        user.profile.hobbies = tags
        user.profile.save()
        return render(request, 'profile/_profile.html')


@login_required
def my_teachers(request):
    listings = request.user.profile.teachers.all()
    return render(request, 'my_teachers.html',
                  {'listings': listings, 'title': 'Favourite Teachers', 'button_name': 'View'})


@login_required
def my_reviews(request):
    reviews = request.user.review_set.all()
    return render(request, 'my_reviews.html',
                  {'reviews': reviews})


@login_required
def send_contact_email(request, list_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=list_id)
        msg = request.POST['message']
        email = request.POST['email']
        if email != '' and msg != '' and listing.email != '':
            t = get_template('emails/contact_email.html')
            context = RequestContext(request, {'msg': msg, 'email': email})
            content = t.render(context)
            msg = EmailMessage('Picasso', content, 'contact@findpicasso.com', [listing.email])
            msg.content_subtype = "html"
            msg.send()
            logger.debug("Email to listing sent by " + email + ' to ' + listing.email)
            return HttpResponse(json.dumps({}), content_type='application/json')
    return HttpResponse("")


@login_required
def change_pic(request):
    if request.method == "POST":
        user = request.user
        f = ContentFile(request.FILES['profile-pic'].read(), name=user.first_name + '.png')
        user.profile.photo = f
        user.profile.save()
        return render(request, 'profile/_profile.html')
    return HttpResponseForbidden('allowed only via POST')


@login_required
def pic_change_listing(request, list_id):
    if request.method == "POST":
        l = Listing.objects.get(pk=list_id)
        f = ContentFile(request.FILES['listing-pic'].read(), name=l.listing_name + '.png')
        l.photo = f
        l.save()
        return HttpResponse(json.dumps({'path': l.photo.name}), content_type='application/json')
    return HttpResponseForbidden('allowed only via POST')