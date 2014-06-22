from django.contrib.auth.models import User
from django.db import models
from picasso.index.models import BaseModel, Listing


class UserProfile(BaseModel):
    user = models.OneToOneField(User, related_name='profile')
    photo = models.ImageField(upload_to='avatars/', null=True)
    location = models.CharField(max_length=10000, default="")
    hobbies = models.CharField(max_length=10000, default="")
    teachers = models.ManyToManyField(Listing)