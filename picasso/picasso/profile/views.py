import json
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import get_template
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
import re
from picasso.index.models import Listing, Address, Tag

# TODO: For all addresses get geocoder


@login_required
def add_listing(request):
    if request.method == "POST":
        listing_name = request.POST['listing_name']
        description = request.POST['description']
        address = request.POST['address']
        postal = request.POST['postal']
        city = request.POST['city']
        email = request.POST['email']
        country = request.POST['country']
        phone = request.POST['phone']
        owner = request.POST['owner']
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
                    tags.append(Tag.objects.create(dash_version=name, tag_name=cat).id)
        if not l_o_e:
            l_o_e = "All"
        else:
            l_o_e = ", ".join(l_o_e)
        price_min = request.POST['price_min']
        price_max = request.POST['price_max']
        active = True if request.POST['active'] == "true" else False
        address = Address.objects.create(city=city, country=country, postal_code=postal, location=address)
        if owner == "true":
            owner = request.user
        else:
            owner = None
        listing = Listing.objects.create(listing_name=listing_name, description=description, address=address,
                                         phone=phone, active=active, owner=owner, created_by=request.user,
                                         level_of_expertise=l_o_e, price_min=price_min, price_max=price_max,
                                         email=email)
        listing.tags = tags
        listing.save()
        return HttpResponse(json.dumps({'id': listing.id}), content_type='application/json')
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
        listing.description = request.POST['description']
        listing.email = request.POST['email']
        listing.address.location = request.POST['address']
        listing.address.postal = request.POST['postal']
        listing.address.city = request.POST['city']
        listing.address.country = request.POST['country']
        listing.address.save()
        listing.phone = request.POST['phone']
        l_o_e = request.POST.getlist('level_of_expertise')
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
        listings = request.user.profile.teachers.all()
        t = get_template('index/listings.html')
        favs = t.render(
            RequestContext(request, {'listings': listings, 'title': 'Favourite Teachers', 'button_name': 'View'}))
        reviews = request.user.review_set.all()
        reviewes = t.render(RequestContext(request, {'reviews': reviews}))
        me_listings = Listing.objects.filter(Q(created_by=request.user) | Q(owner=request.user))
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
    listing = Listing.objects.get(pk=list_id)
    msg = request.POST['message']
    email = request.POST['email']
    if email != '' and msg != '' and listing.email != '':
        t = get_template('emails/contact_email.html')
        context = RequestContext(request, )
        t.render(context)



@login_required
def change_pic(request):
    if request.method == "POST":
        user = request.user
        f = ContentFile(request.FILES['profile-pic'].read(), name=user.first_name + '.png')
        user.profile.photo = f
        user.profile.save()
        return render(request, 'profile/_profile.html')
    return HttpResponseForbidden('allowed only via POST')