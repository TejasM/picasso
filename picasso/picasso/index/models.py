from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import re


class BaseModel(models.Model):
    create_time = models.DateTimeField(default=timezone.now())


class Tag(BaseModel):
    tag_name = models.CharField(default="", max_length=500)

    @property
    def dash_version(self):
        return self.tag_name.replace(' ', '-').replace(',', '-').replace('/', '-').lower()


class Address(BaseModel):
    city = models.CharField(default="Toronto", max_length=1000)
    country = models.CharField(default="Canada", max_length=100)
    location = models.CharField(default="", max_length=1000)
    postal_code = models.CharField(default="", max_length=100)

    def __unicode__(self):
        string = ""
        string += self.location
        if self.location != "":
            string += "<br>"
        string += self.city + ", " + self.country
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
                '/', '').lower()
        else:
            return "Unknown"

    @property
    def get_unique_url(self):
        string = "/"
        if self.tags.count() != 0:
            string += self.tags.all().order_by('?')[0].tag_name.replace(' ', '').replace(',', '').replace('-',
                                                                                                          '').replace(
                '/', '').lower()
        else:
            string += "unknown"
        string += "/" + self.unique_url
        return string

    @property
    def get_listing_name(self):
        return self.listing_name.replace(' ', '').replace(',', '').replace('-', '').replace('/', '')

    def save(self, **kwargs):
        # count = Listing.objects.filter(listing_name=self.listing_name).count()
        # if count == 1:
        #     self.unique_url = re.sub(r'\W+', '-', self.listing_name) + "-" + self.address.city.split(',')[0]
        # else:
        #     count = 0
        #     for l in Listing.objects.filter(listing_name=self.listing_name):
        #         if l.unique_url != '':
        #             count += 1
        #     self.unique_url = re.sub(r'\W+', '-', self.listing_name) + "-" + self.address.city.split(',')[
        #         0] + "-" + str(count)
        super(Listing, self).save(**kwargs)


class Review(BaseModel):
    comment = models.CharField(default="", max_length=10000)
    rating = models.FloatField(default=-1)
    user = models.ForeignKey(User, default=None, null=True)
    listing = models.ForeignKey(Listing)