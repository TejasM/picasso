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
    tag_name = models.CharField(default="", max_length=500)
    possible_folders = models.CharField(default="", max_length=500)
    dash_version = models.CharField(default="", max_length=500)

    def save(self, **kwargs):
        self.dash_version = re.sub(r'\W+', '-', self.tag_name).lower()
        super(Tag, self).save(**kwargs)

    def __unicode__(self):
        return self.tag_name


class Address(BaseModel):
    city = models.CharField(default="Toronto", max_length=1000)
    country = models.CharField(default="Canada", max_length=100)
    location = models.CharField(default="", max_length=1000)
    postal_code = models.CharField(default="", max_length=100)
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


def get_unique_url(instance):
    count = Listing.objects.filter(listing_name=instance.listing_name).count()
    if count == 0:
        return instance.listing_name.replace(' ', '-').replace(',', '-').replace('/', '-')
    else:
        return instance.listing_name.replace(' ', '-').replace(',', '-').replace('/', '-') + str(count)


class Listing(BaseModel):
    listing_name = models.CharField(default="", max_length=500)
    school_name = models.CharField(default="", max_length=500)
    description = models.CharField(default="", max_length=10000)
    tags = models.ManyToManyField(Tag)
    address = models.ForeignKey(Address, default=None, null=True)
    price = models.FloatField(default=0)
    scraped_url = models.CharField(default="", max_length=10000)
    active = models.BooleanField(default=True)
    email = models.EmailField(default="", blank=True, null=True)
    phone = models.CharField(default="", blank=True, null=True, max_length=20)
    created_by = models.ForeignKey(User, null=True, default=None, related_name='creator')
    owner = models.ForeignKey(User, null=True, default=None, related_name='owner')
    unique_url = models.CharField(max_length=1000, default="")
    last_modified = models.DateTimeField(default=timezone.now())

    hash_key = models.CharField(max_length=40, default=hashlib.sha1(os.urandom(128)).hexdigest())

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
        if self.tags.count() != 0:
            return ", ".join(self.tags.values_list('tag_name', flat=True))
        else:
            return "Unknown"

    @property
    def get_string_tags_no_comma(self):
        if self.tags.count() != 0:
            return " ".join(self.tags.values_list('tag_name', flat=True))
        else:
            return "Unknown"

    @property
    def get_string_tags_no_space(self):
        if self.tags.count() != 0:
            return self.tags.all().order_by('?')[0].tag_name.replace(' ', '').replace(',', '').replace('-', '').replace(
                '/', '').lower().strip()
        else:
            return "Unknown"

    @property
    def get_unique_url(self):
        string = "/"
        if self.tags.count() != 0:
            string += self.tags.all().order_by('?')[0].dash_version
        else:
            string += "unknown"
        string += "/" + self.unique_url
        return string

    @property
    def get_listing_name(self):
        return self.listing_name.replace(' ', '').replace(',', '').replace('-', '').replace('/', '')

    @property
    def get_photo_url(self):
        if self.tags.count() != 0:
            for tag in self.tags.all():
                if tag.tag_name.strip().lower() in STATIC_IMAGE_URLS:
                    return random.choice(STATIC_IMAGE_URLS[tag.tag_name.strip().lower()])
        return random.choice(STATIC_IMAGE_URLS['music'])

    @permalink
    def get_absolute_url(self):
        if self.tags.count() != 0:
            string = self.tags.all().order_by('?')[0].dash_version
        else:
            string = "unknown"
        return (string, [self.unique_url])

    def save(self, **kwargs):
        count = Listing.objects.filter(listing_name=self.listing_name).count()
        if self.address:
            address = self.address.city.split(',')[0]
        else:
            address = ''
        if count == 1:
            if address != '':
                self.unique_url = re.sub(r'\W+', '-', self.listing_name) + "-" + address
            else:
                self.unique_url = re.sub(r'\W+', '-', self.listing_name) + "-" + str(count)
        else:
            count = 0
            for l in Listing.objects.filter(listing_name=self.listing_name):
                if l.unique_url != '':
                    count += 1
            if address != '':
                self.unique_url = re.sub(r'\W+', '-', self.listing_name) + "-" + address + "-" + str(count)
            else:
                self.unique_url = re.sub(r'\W+', '-', self.listing_name) + "-" + str(count)
        super(Listing, self).save(**kwargs)


admin.site.register(Listing)
admin.site.register(Tag)


class Review(BaseModel):
    comment = models.CharField(default="", max_length=10000)
    rating = models.FloatField(default=-1)
    user = models.ForeignKey(User, default=None, null=True)
    listing = models.ForeignKey(Listing)


watson.register(Listing,
                fields=('tags__tag_name', 'listing_name', 'school_name', 'description', 'scraped_url', 'unique_url',
                        'address__city', 'address__country', 'owner__first_name', 'owner__last_name', 'owner__email',
                        'address__location'))
watson.register(Tag)
watson.register(Review)
watson.register(Address)