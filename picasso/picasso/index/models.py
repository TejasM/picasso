from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    create_time = models.DateTimeField(default=timezone.now())


class Tag(BaseModel):
    tag_name = models.CharField(default="", max_length=500)


class Address(BaseModel):
    city = models.CharField(default="Toronto", max_length=100)
    country = models.CharField(default="Canada", max_length=100)
    address = models.CharField(default="", max_length=100)


class Listing(BaseModel):
    listing_name = models.CharField(default="", max_length=500)
    description = models.CharField(default="", max_length=10000)
    tags = models.ManyToManyField(Tag)
    address = models.ForeignKey(Address, default=None, null=True)
    price = models.FloatField(default=0)
    scraped_url = models.CharField(default="")

    @property
    def get_price(self):
        if self.price != 0:
            return self.price
        return "N/A"


class Review(BaseModel):
    comment = models.CharField(default="", max_length=10000)
    rating = models.FloatField(default=-1)
    listing = models.ForeignKey(Listing)