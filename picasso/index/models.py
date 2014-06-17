from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    create_time = models.DateTimeField(default=timezone.now())


class Tag(BaseModel):
    tag_name = models.CharField(default="", max_length=500)


class Listing(BaseModel):
    listing_name = models.CharField(default="", max_length=500)
    description = models.CharField(default="", max_length=10000)
    tags = models.ManyToManyField(Tag)


class Review(BaseModel):
    comment = models.CharField(default="", max_length=10000)
    rating = models.FloatField(default=-1)
    listing = models.ForeignKey(Listing)