import hashlib
import os
import random
import re

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.gis import geos
from django.db import models
from django.db.models import Avg, permalink
from django.utils import timezone
from pygeocoder import Geocoder
from pygeolib import GeocoderError
import watson
from django.contrib.gis.db import models as gis_models


STATIC_IMAGE_URLS = {
    'music': ['/static/images/photos/music/music_0.jpg', '/static/images/photos/music/music_1.jpg',
              '/static/images/photos/music/music_2.jpg'],
    'piano': ['/static/images/photos/piano/piano_0.jpg', '/static/images/photos/piano/piano_1.jpg',
              '/static/images/photos/piano/piano_2.jpg', '/static/images/photos/piano/piano_3.jpg',
              '/static/images/photos/piano/piano_4.jpg', '/static/images/photos/piano/piano_5.jpg'],
    'brass': ['/static/images/photos/brass/brass_0.png'],
    'drums': ['/static/images/photos/drums/drums_0.jpg', '/static/images/photos/drums/drums_1.png'],
}


class BaseModel(models.Model):
    create_time = models.DateTimeField(default=timezone.now())


class Tag(BaseModel):
    tag_name = models.CharField(default="", max_length=500, blank=True)
    possible_folders = models.CharField(default="", max_length=500, blank=True)
    dash_version = models.CharField(default="", max_length=500, blank=True)
    parent_tag = models.ForeignKey('Tag', default=None, null=True, blank=True)
    visible = models.BooleanField(default=True)

    def save(self, **kwargs):
        self.dash_version = re.sub(r'\W+', '-', self.tag_name).lower()
        super(Tag, self).save(**kwargs)

    def __unicode__(self):
        if self.visible:
            return self.tag_name
        else:
            return ''


class Address(BaseModel):
    city = models.CharField(default="Toronto", max_length=1000)
    country = models.CharField(default="Canada", max_length=100)
    location = models.CharField(default="", max_length=1000)
    postal_code = models.CharField(default="", max_length=100)
    state = models.CharField(default="Ontario", max_length=100)
    point = gis_models.PointField(u"longitude/latitude",
                                  geography=True, blank=True, null=True)

    objects = gis_models.GeoManager()

    def __unicode__(self):
        string = ""
        string += self.location
        if self.location != "":
            string += "<br>"
        if self.city != '':
            string += self.city + ", " + self.country
        else:
            string += self.country
        if self.postal_code != "":
            string += "<br>" + self.postal_code
        return string

    def get_obscure(self):
        string = ""
        if self.city != '':
            string += self.city + ", " + self.country
        else:
            string += self.country
        if self.postal_code != "":
            string += "<br>" + self.postal_code
        return string

    def save(self, **kwargs):
        if self.point is not None:
            try:
                results = Geocoder.geocode(
                    str(
                        self.location + ' ' + self.state + ' ' + self.city + ' ' + self.country + ' ' + self.postal_code))
                lat, lon = results[0].coordinates
            except IndexError:
                lat, lon = 43.7, -79.4
            except GeocoderError:
                lat, lon = 43.7, -79.4
            self.point = "POINT(%s %s)" % (lon, lat)
        super(Address, self).save(**kwargs)


def get_unique_url(instance):
    count = Listing.objects.filter(listing_name=instance.listing_name).count()
    if count == 0:
        return instance.listing_name.replace(' ', '-').replace(',', '-').replace('/', '-')
    else:
        return instance.listing_name.replace(' ', '-').replace(',', '-').replace('/', '-') + str(count)


def generate_hash():
    return hashlib.sha1(os.urandom(128)).hexdigest()


class Listing(BaseModel):
    listing_name = models.CharField(default="", max_length=500)
    class_name = models.CharField(default="", max_length=500)
    place_name = models.CharField(default="", max_length=500)
    description = models.CharField(default="", max_length=10000)
    tags = models.ManyToManyField(Tag, related_name='listings')
    address = models.ForeignKey(Address, default=None, null=True)
    price = models.FloatField(default=0)
    scraped_url = models.CharField(default="", max_length=10000)
    active = models.BooleanField(default=True)
    email = models.EmailField(default="", blank=True, null=True)
    phone = models.CharField(default="", blank=True, null=True, max_length=100)
    created_by = models.ForeignKey(User, null=True, default=None, related_name='creator')
    owner = models.ForeignKey(User, null=True, default=None, related_name='owner')
    unique_url = models.CharField(max_length=1000, default="")
    last_modified = models.DateTimeField(default=timezone.now())
    website = models.CharField(default="", max_length=1000)
    point = gis_models.PointField(u"longitude/latitude",
                                  geography=True, blank=True, null=True)

    inner_point = gis_models.PointField(u"longitude/latitude",
                                  geography=True, blank=True, null=True)

    total_rating = models.FloatField(default=0)

    hash_key = models.CharField(max_length=100, default=generate_hash, unique=True)

    photo = models.ImageField(upload_to='listings/', null=True, blank=True, default=None)
    visible = models.BooleanField(default=True)

    level_of_expertise = models.CharField(default="All", max_length=100)
    price_min = models.FloatField(default=0)
    price_max = models.FloatField(default=0)

    objects = gis_models.GeoManager()
    PLACE_CHOICES = (
        ('Pri', 'Private'),
        ('Sch', 'School'),
    )
    place = models.CharField(max_length=3, choices=PLACE_CHOICES, default='Pri')

    @property
    def get_full_listing_name(self):
        string = ''
        string += self.listing_name
        if string != '' and self.class_name != '':
            string += ' for ' + self.class_name
        else:
            string += self.class_name
        if string != '' and self.place_name != '':
            string += ' at ' + self.place_name
        return string

    @property
    def get_price(self):
        if self.price != 0:
            return self.price
        return "N/A"

    @property
    def get_rating(self):
        if self.review_set.count() != 0:
            return self.review_set.aggregate(Avg('rating')).values()[0]
        return "N/A"

    @property
    def get_string_tags(self):
        if self.tags.filter(visible=True).count() != 0:
            string_list = self.tags.filter(visible=True).values_list('tag_name', flat=True)
            # for t in self.tags.filter(visible=True):
            # if t.parent_tag is not None:
            # string_list.append(t.parent_tag.tag_name)
            return ", ".join(string_list)
        else:
            return "Unknown"

    @property
    def get_parent_tag(self):
        if self.tags.filter(visible=True).count() != 0:
            for t in self.tags.filter(visible=True):
                if t.parent_tag is not None:
                    return t.parent_tag.tag_name
        else:
            return None

    @property
    def get_string_tags_no_comma(self):
        if self.tags.filter(visible=True).count() != 0:
            string_list = self.tags.filter(visible=True).values_list('tag_name', flat=True)
            for t in self.tags.filter(visible=True):
                if t.parent_tag is not None:
                    string_list.append(t.parent_tag.tag_name)
            return " ".join(string_list)
        else:
            return "Unknown"

    @property
    def get_string_tags_no_space(self):
        if self.tags.filter(visible=True).count() != 0:
            return self.tags.filter(visible=True).order_by('?')[0].tag_name.replace(' ', '').replace(',', '').replace(
                '-', '').replace(
                '/', '').lower().strip()
        else:
            return "Unknown"

    @property
    def get_unique_url(self):
        string = "/"
        if self.tags.filter(visible=True).count() != 0:
            string += self.tags.filter(visible=True).order_by('?')[0].dash_version
        else:
            string += "unknown"
        string += "/" + self.unique_url
        return string

    @property
    def get_listing_name(self):
        return self.listing_name.replace(' ', '').replace(',', '').replace('-', '').replace('/', '')

    @property
    def get_photo_url(self):
        if self.tags.filter(visible=True).count() != 0:
            for tag in self.tags.filter(visible=True).all():
                if tag.tag_name.strip().lower() in STATIC_IMAGE_URLS:
                    return random.choice(STATIC_IMAGE_URLS[tag.tag_name.strip().lower()])
        return random.choice(STATIC_IMAGE_URLS['music'])

    @permalink
    def get_absolute_url(self):
        if self.tags.filter(visible=True).count() != 0:
            string = self.tags.filter(visible=True).all().order_by('?')[0].dash_version
        else:
            string = "unknown"
        return ('actual_listing', [string, self.unique_url])

    def save(self, **kwargs):
        count = Listing.objects.filter(listing_name=self.listing_name).count()
        if self.address:
            address = re.sub(r'\W+', '-', self.address.city.split(',')[0])
        else:
            address = ''
        if count == 1:
            if address != '':
                self.unique_url = re.sub(r'\W+', '-', self.get_full_listing_name) + "-" + address
            else:
                self.unique_url = re.sub(r'\W+', '-', self.get_full_listing_name) + "-" + str(count)
        else:
            count = 0
            for l in Listing.objects.filter(listing_name=self.listing_name):
                if l.unique_url != '':
                    count += 1
            if address != '':
                self.unique_url = re.sub(r'\W+', '-', self.get_full_listing_name) + "-" + address + "-" + str(count)
            else:
                self.unique_url = re.sub(r'\W+', '-', self.get_full_listing_name) + "-" + str(count)
        if self.review_set.count() != 0:
            self.total_rating = self.review_set.aggregate(Avg('rating')).values()[0]
        else:
            self.total_rating = 0
        #self.hash_key = generate_hash
        if self.address is not None:
            self.inner_point = self.address.point
        super(Listing, self).save(**kwargs)


admin.site.register(Listing)
admin.site.register(Tag)


class Review(BaseModel):
    comment = models.CharField(default="", max_length=10000)
    rating = models.FloatField(default=-1)
    user = models.ForeignKey(User, default=None, null=True)
    listing = models.ForeignKey(Listing)


watson.register(Listing,
                fields=(
                    'tags__tag_name', 'listing_name', 'class_name', 'place_name', 'description', 'scraped_url',
                    'unique_url',
                    'email',))
watson.register(Tag)
watson.register(Review)
watson.register(Address)