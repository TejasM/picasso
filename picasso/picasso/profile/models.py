from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from picasso.index.models import BaseModel, Listing


class UserProfile(BaseModel):
    user = models.OneToOneField(User, related_name='profile')
    photo = models.ImageField(upload_to='avatars/', null=True)
    location = models.CharField(max_length=10000, default="")
    hobbies = models.CharField(max_length=10000, default="")
    teachers = models.ManyToManyField(Listing)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)